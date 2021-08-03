import pandas as pd
import numpy as np
import datetime
import pytz

def percent_change(current,previous):
    return 100*(current-previous)/previous