import logging
import re

from .extractor import TemplateExtractor

logger = logging.getLogger(__name__)


POSSIBLE_LABELS = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "ab": "5",
    "ad": "6"
}


def from_template(template):
    template_name = normalize_template_name(template.name)
    if template_name == "marca de projeto":
        label = extract_label(template)
        if label is not None:
            yield ("marca de projeto", label)


def extract_label(template):
    try:
        label = template.get("qualidade").value
    except ValueError:
        try:
            label = template.get(1).value
        except ValueError:
            label = None
    if label != "?":
        label = normalize_label(label)
        if label is None:
            logger.warn("Could not extract label from {0}".format(str(template)))
        else:
            return label



def normalize_label(label):
    label = label.lower()
    if label in POSSIBLE_LABELS:
        return POSSIBLE_LABELS[label]
    else:
        return None


def normalize_template_name(template_name):
    return template_name.lower().replace("_", " ")


ptwiki = TemplateExtractor(
    __name__,
    doc="""
articlequality.extractors.ptwiki
++++++++++++++++++++++++++++++++
This extractor looks for instances of templates that contain
"class=<some class>" on article talk pages (namespace = 1) and parses the
template name to obtain a `project`.
""",
    namespaces={1},
    from_template=from_template
)
