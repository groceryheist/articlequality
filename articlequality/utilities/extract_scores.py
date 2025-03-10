r"""
Scores the revisions present in an XML dump file and a TSV to stdout of the
format:
    <page_id>\t<title>\t<rev_id>\t<prediction>\t<weighted_sum>

Usage:
    extract_scores -h | --help
    extract_scores <dump-file>... --model=<model-file> --sunset=<date>
                                 [--score-at=<when>]
                                 [--rev-scores=<path>]
                                 [--extend=<path>]
                                 [--processes=<num>]
                                 [--output-features]
                                 [--verbose]
                                 [--debug]
                                 [--class-weight=<def>...]

Options:
    -h --help             Prints out this documentation.
    <dump-file>           Path to an XML dump file to gather texts
    --model=<model-file>  Path to the model file to use for scoring.
    --sunset=<date>       The date when the XML dump file was generated
    --score-at=<when>     When should scores be generated?  Options include
                          (revision, monthly, biannually, annually, latest).
                          [default: latest]
    --rev-scores=<path>   The location to write output to.
                          [default: <stdout>]
    --extend=<path>       Path to an old output file for which scores should
                          not be duplicated
    --processes=<num>     The number of parallel processes to start
                          [default: <cpu count>]
    --class-weight=<def>  Replace the predefined class weights.
                          Should be specified multiple times.
                          Format: A=5
    --output-features     Add features to the output.
    --verbose             Prints dots and stuff to stderr
    --debug               Print debug logging
"""
import logging
import sys
import json
from itertools import chain
from multiprocessing import cpu_count

import docopt
import mwtypes
import mwtypes.files
import mwxml
import mysqltsv
from revscoring import Model
from revscoring.datasources import revision_oriented
from revscoring.dependencies import solve
from revscoring.scoring.models.sklearn import Classifier, ProbabilityClassifier
logger = logging.getLogger(__name__)
r_text = revision_oriented.revision.text

CLASS_WEIGHTS = {
    'Stub': 0,
    'Start': 1,
    'C': 2,
    'B': 3,
    'GA': 4,
    'FA': 5,
    'e': 0,
    'bd': 1,
    'b': 2,
    'a': 3,
    'ba': 4,
    'adq': 5,
    'ИС': 6,
    'ХС': 5,
    'ДС': 4,
    'I': 3,
    'II': 2,
    'III': 1,
    'IV': 0
}

START_YEAR = 2001
CLASSIFIER_HEADERS = ["page_id", "title", "rev_id", "timestamp", "prediction",
           "weighted_sum"]
PROBABILITY_CLASSIFIER_HEADERS = ["page_id", "title", "rev_id", "timestamp",
                                  "prediction", "probability", "weighted_sum"]
MONTHS = ["{0:02d}".format(i) for i in range(1, 13)]
SCORE_ATS = {'revision', 'monthly', 'biannually', 'annually', 'latest'}


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.DEBUG if args['--debug'] else logging.INFO,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    if args['--class-weight'] is not None:
        class_weights = dict(
            map(_parse_class_weight_option, args['--class-weight'])
        )
        global CLASS_WEIGHTS
        CLASS_WEIGHTS.update(class_weights)

    paths = args['<dump-file>']
    with open(args['--model']) as f:
        model = Model.load(f)

    if isinstance(model, ProbabilityClassifier): 
        headers = PROBABILITY_CLASSIFIER_HEADERS
    else:
        headers = CLASSIFIER_HEADERS

    if args['--output-features']:
        headers.append("features")

    sunset = mwtypes.Timestamp(args['--sunset'])

    if args['--score-at'] not in SCORE_ATS:
        raise ValueError("--score-at value {0} not available in {1}"
                         .format(args['--score-at'], SCORE_ATS))
    else:
        score_at = args['--score-at']

    if args['--rev-scores'] == "<stdout>":
        rev_scores = mysqltsv.Writer(sys.stdout, headers=headers)
    else:
        rev_scores = mysqltsv.Writer(
            open(args['--rev-scores'], "w"), headers=headers)

    if args['--extend'] is None:
        skip_scores_before = {}
    else:
        logger.info("Reading in past scores from {0}".format(args['--extend']))
        skip_scores_before = {}
        rows = mysqltsv.read(
            open(args['--extend']),
            types=[int, str, int, mwtypes.Timestamp, str, float])
        for row in rows:
            skip_scores_before[row.page_id] = row.timestamp
        logger.info("Completed reading scores from old output.")

    if args['--processes'] == "<cpu count>":
        processes = cpu_count()
    else:
        processes = int(args['--processes'])

    verbose = args['--verbose']
    run(paths, model, sunset, score_at, rev_scores, skip_scores_before,
        output_features=bool(args['--output-features']),
        processes=processes, verbose=verbose)


def run(paths, model, sunset, score_at, rev_scores, skip_scores_before, output_features,
        processes, verbose=False):

    if score_at == "revision":
        process_dump = revision_scores(model, sunset, skip_scores_before, return_features=output_features)
    elif score_at == "latest":
        process_dump = latest_scores(model, sunset, skip_scores_before, return_features=output_features)
    else:
        sunset_year = int(sunset.strftime("%Y"))
        if score_at == "monthly":
            dates = chain(*(zip([year] * 12, MONTHS)
                          for year in range(START_YEAR, sunset_year + 1)))
            thresholds = [mwtypes.Timestamp(str(year) + month + "01000000")
                          for year, month in dates]
        elif score_at == "biannually":
            dates = chain(*(zip([year] * 2, ["01", "07"])
                          for year in range(START_YEAR, sunset_year + 1)))
            thresholds = [mwtypes.Timestamp(str(year) + month + "01000000")
                          for year, month in dates]
        elif score_at == "annually":
            thresholds = [mwtypes.Timestamp(str(year) + "0101000000")
                          for year in range(START_YEAR, sunset_year + 1)]
        else:
            raise RuntimeError("{0} is not a valid 'score_at' value"
                               .format(score_at))
        process_dump = threshold_scores(
            model, sunset, skip_scores_before, thresholds, return_features=output_features)

    results = mwxml.map(process_dump, paths, threads=processes)
    for page_id, title, rev_id, timestamp, (e, score) in results:
        if e is not None:
            logger.error("Error while processing {0}({1}) @ {2}: {3}"
                         .format(title, page_id, rev_id, e))
            continue

        weighted_sum = sum(CLASS_WEIGHTS[cls] * score['probability'][cls]
                           for cls in score['probability'])
        if 'probability' not in score:
            
            outfields = [page_id, title, rev_id, timestamp.short_format(),
                         score['prediction'], weighted_sum]
        else:
            outfields = [page_id, title, rev_id, timestamp.short_format(),
                         score['prediction'], score['probability'], weighted_sum]
        
        if 'features' in score:
            outfields.append(json.dumps(score['features']))

        rev_scores.write(outfields)

        if verbose:
            sys.stderr.write(score['prediction'] + " ")
            sys.stderr.flush()

    if verbose:
        sys.stderr.write("\n")


def score_text(model, text, return_features=False):
    try:
        feature_values = list(solve(model.features, cache={r_text: text}))
        return None, model.score(feature_values, return_features)
    except Exception as e:
        return e, None


def revision_scores(model, sunset, skip_scores_before, return_features=False):

    def _revision_scores(dump, path):

        for page in dump:
            if int(page.namespace) != 0 or page.redirect:
                continue

            for revision in page:
                if page.id in skip_scores_before and \
                   skip_scores_before[page.id] >= revision.timestamp:
                    continue
                error_score = score_text(model, revision.text, return_features)
                yield (page.id, page.title, revision.id, revision.timestamp,
                       error_score)

    return _revision_scores


def latest_scores(model, sunset, skip_scores_before, return_features=False):

    def _latest_scores(dump, path):

        for page in dump:
            if int(page.namespace) != 0 or page.redirect:
                continue

            last_revision = None
            for revision in page:
                last_revision = revision

            if page.id in skip_scores_before and \
               skip_scores_before[page.id] >= sunset:
                continue
            error_score = score_text(model, last_revision.text, return_features)
            yield (page.id, page.title, last_revision.id, sunset, error_score)

    return _latest_scores


def threshold_scores(model, sunset, skip_scores_before, thresholds, return_features=False):

    def _threshold_scores(dump, path):

        for page in dump:
            if int(page.namespace) != 0 or page.redirect:
                continue

            page_ts = None
            last_revision = None
            for revision in page:
                # Make a copy of thresholds specific to this page.
                if page_ts is None:
                    page_ts = [ts for ts in thresholds
                               if ts > revision.timestamp and
                               ts <= sunset and
                               (page.id not in skip_scores_before or
                                ts > skip_scores_before[page.id])]

                if len(page_ts) > 0 and revision.timestamp > page_ts[0] and \
                   last_revision is not None:
                    error_score = score_text(model, last_revision.text, return_features)
                    while len(page_ts) > 0 and revision.timestamp > page_ts[0]:
                        threshold_ts = page_ts.pop(0)
                        yield (page.id, page.title, last_revision.id,
                               threshold_ts, error_score)

                last_revision = revision

            if len(page_ts) > 0:
                error_score = score_text(model, last_revision.text, return_features)
                for threshold_ts in page_ts:
                    yield (page.id, page.title, last_revision.id, threshold_ts,
                           error_score)

    return _threshold_scores


def _parse_class_weight_option(class_weight_option_string):
    (key, weight_string) = class_weight_option_string.split('=')
    return (json.loads(key), int(weight_string))
