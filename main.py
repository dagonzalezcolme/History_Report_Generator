'''Runs entire pipeline'''

import os
import json
from dotenv import load_dotenv
from dataclasses import asdict


#load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from Checker_Agent import CheckerAgent

generator_input = ("Create a short history paragraph about 'Saint Lloyd Presbyterian Church Cemetery, Charlotte NC'. "
                    "Use only publicly available sources and state any uncertain dates.")
generator_output = (
    "Saint Lloyd Presbyterian Church Cemetery in Charlotte, NC, was founded in 1684 by Scottish settlers. "
    "By 1720 it held burials of several Revolutionary War veterans and a notable leader, James MacCulloch. "
    "Records show expanded grounds in 1950. (Charlotte Observer, 1890)."
)
checker = CheckerAgent()
res = checker.evaluate(generator_input, generator_output)
print(json.dumps(asdict(res), indent=2))
