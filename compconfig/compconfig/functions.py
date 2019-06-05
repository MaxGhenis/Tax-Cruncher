import os
import json
import traceback
import paramtools
import pandas as pd
from .helpers import convert_defaults, convert_adj
import inspect
from taxcrunch.cruncher import Cruncher, CruncherParams
from taxcalc import Policy
from IPython.display import HTML

TCPATH = inspect.getfile(Policy)
TCDIR = os.path.dirname(TCPATH)

with open(os.path.join(TCDIR, "policy_current_law.json"), "r") as f:
    pcl = json.loads(f.read())

RES = convert_defaults(pcl)


class TCParams(paramtools.Parameters):
    defaults = RES


def get_inputs(meta_params_dict):
    """
	Return default parameters from Tax-Cruncher
	"""
    params = CruncherParams()
    policy_params = TCParams()

    keep = [
        "mstat",
        "page",
        "sage",
        "depx",
        "dep13",
        "dep17",
        "dep18",
        "pwages",
        "swages",
        "dividends",
        "intrec",
        "stcg",
        "ltcg",
        "otherprop",
        "nonprop",
        "pensions",
        "gssi",
        "ui",
        "proptax",
        "otheritem",
        "childcare",
        "mortgage",
        "mtr_options"
    ]
    full_dict = params.specification(
        meta_data=True, include_empty=True, serializable=True
    )

    params_dict = {var: full_dict[var] for var in keep}

    cruncher_params = params_dict

    pol_params = policy_params.specification(
        meta_data=True, include_empty=True, serializable=True, year=2019
    )

    return {}, {"Tax Information": cruncher_params, "Policy": pol_params}


def validate_inputs(meta_params_dict, adjustment, errors_warnings):
    params = CruncherParams()
    params.adjust(adjustment["Tax Information"], raise_errors=False)
    errors_warnings["Tax Information"]["errors"].update(params.errors)

    pol_params = {}
    # drop checkbox parameters.
    for param, data in list(adjustment["Policy"].items()):
        if not param.endswith("checkbox"):
            pol_params[param] = data

    policy_params = TCParams()
    policy_params.adjust(pol_params, raise_errors=False)
    errors_warnings["Policy"]["errors"].update(policy_params.errors)

    return errors_warnings


def run_model(meta_params_dict, adjustment):
    params = CruncherParams()
    params.adjust(adjustment["Tax Information"], raise_errors=False)
    newvals = params.specification()

    pol_params = TCParams()
    pol_params.adjust(adjustment["Policy"], raise_errors=False)

    crunch = Cruncher(inputs=newvals, custom_reform=pol_params)

    return comp_output(crunch)


def comp_output(crunch):
    basic = crunch.basic_table()
    detail = crunch.calc_table()

    style = """
		<style>
        	.body tbody tr:nth-child(even) { background-color: #e8e9ea; }
        	.head thead { background-color: #cfe3f7; }
        	.rhover tbody tr:hover { background-color: #e0e0e0 !important; }
    	</style>
    	"""

    table_basic = style + basic.to_html(
        classes="body head rhover", col_space=150, index=False, justify="center"
    )
    table_detail = style + detail.to_html(
        classes="body head rhover", col_space=150, index=False, justify="center"
    )

    comp_dict = {
        "model_version": "1.0.0",
        "renderable": [
            {"media_type": "table", "title": "Basic Liabilities", "data": table_basic},
            {
                "media_type": "table",
                "title": "Calculation of Liabilities",
                "data": table_detail,
            },
        ],
        "downloadable": [],
    }
    return comp_dict