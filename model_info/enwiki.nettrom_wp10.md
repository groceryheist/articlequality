Model Information:
	 - type: GradientBoosting
	 - version: 0.9.2
	 - params: {'scale': True, 'center': True, 'labels': ['Stub', 'Start', 'C', 'B', 'GA', 'FA'], 'multilabel': False, 'population_rates': None, 'ccp_alpha': 0.0, 'criterion': 'friedman_mse', 'init': None, 'learning_rate': 0.01, 'loss': 'log_loss', 'max_depth': 7, 'max_features': 'log2', 'max_leaf_nodes': None, 'min_impurity_decrease': 0.0, 'min_samples_leaf': 1, 'min_samples_split': 2, 'min_weight_fraction_leaf': 0.0, 'n_estimators': 500, 'n_iter_no_change': None, 'random_state': None, 'subsample': 1.0, 'tol': 0.0001, 'validation_fraction': 0.1, 'verbose': 0, 'warm_start': False, 'label_weights': None}
	Environment:
	 - revscoring_version: '2.11.13'
	 - platform: 'Linux-6.12.9+bpo-amd64-x86_64-with-glibc2.36'
	 - machine: 'x86_64'
	 - version: '#1 SMP PREEMPT_DYNAMIC Debian 6.12.9-1~bpo12+1 (2025-01-19)'
	 - system: 'Linux'
	 - processor: ''
	 - python_build: ('main', 'Feb 12 2025 14:51:05')
	 - python_compiler: 'Clang 19.1.6 '
	 - python_branch: ''
	 - python_implementation: 'CPython'
	 - python_revision: ''
	 - python_version: '3.11.11'
	 - release: '6.12.9+bpo-amd64'
	
	Statistics:
	counts (n=32182):
		label       n         ~Stub    ~Start    ~C    ~B    ~GA    ~FA
		-------  ----  ---  -------  --------  ----  ----  -----  -----
		'Stub'   5361  -->     4530       795    24    11      1      0
		'Start'  5423  -->      704      3493   826   337     61      2
		'C'      5449  -->       71       979  2691  1031    591     86
		'B'      5464  -->       38       666  1350  2175    894    341
		'GA'     5491  -->        3        49   327   340   3487   1285
		'FA'     4994  -->        1         2    26   246    933   3786
	rates:
		              'Stub'    'Start'    'C'    'B'    'GA'    'FA'
		----------  --------  ---------  -----  -----  ------  ------
		sample         0.167      0.169  0.169  0.17    0.171   0.155
		population     0.576      0.322  0.054  0.035   0.01    0.003
	match_rate (micro=0.386, macro=0.189):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		   0.5    0.271  0.117  0.085  0.098  0.065
	filter_rate (micro=0.614, macro=0.811):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		   0.5    0.729  0.883  0.915  0.902  0.935
	recall (micro=0.743, macro=0.629):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		 0.845    0.644  0.494  0.398  0.635  0.758
	!recall (micro=0.944, macro=0.925):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		  0.97    0.907  0.905  0.926  0.907  0.937
	precision (micro=0.827, macro=0.371):
		  Stub    Start     C      B     GA     FA
		------  -------  ----  -----  -----  -----
		 0.974    0.767  0.23  0.162  0.063  0.031
	!precision (micro=0.844, macro=0.934):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		 0.821    0.843  0.969  0.977  0.996  0.999
	f1 (micro=0.773, macro=0.387):
		  Stub    Start      C     B     GA     FA
		------  -------  -----  ----  -----  -----
		 0.905      0.7  0.313  0.23  0.115  0.059
	!f1 (micro=0.89, macro=0.928):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		 0.889    0.874  0.936  0.951  0.949  0.967
	accuracy (micro=0.873, macro=0.892):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		 0.898    0.822  0.882  0.908  0.904  0.936
	fpr (micro=0.056, macro=0.075):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		  0.03    0.093  0.095  0.074  0.093  0.063
	roc_auc (micro=0.942, macro=0.905):
		  Stub    Start      C      B     GA     FA
		------  -------  -----  -----  -----  -----
		 0.978    0.904  0.856  0.832  0.909  0.955
	pr_auc (micro=0.84, macro=0.397):
		  Stub    Start     C      B     GA     FA
		------  -------  ----  -----  -----  -----
		 0.983    0.785  0.25  0.173  0.118  0.075
	
	 - score_schema: {'title': 'Scikit learn-based classifier score with probability', 'type': 'object', 'properties': {'prediction': {'description': 'The most likely label predicted by the estimator', 'type': 'string'}, 'probability': {'description': 'A mapping of probabilities onto each of the potential output labels', 'type': 'object', 'properties': {'Stub': {'type': 'number'}, 'Start': {'type': 'number'}, 'C': {'type': 'number'}, 'B': {'type': 'number'}, 'GA': {'type': 'number'}, 'FA': {'type': 'number'}}}}}

