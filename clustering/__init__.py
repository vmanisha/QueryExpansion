from utils import text_to_vector
import sys
import os, random
from subprocess import call
import json
from utils import stopSet
from features.featureManager import FeatureManager
from nltk import stem
from clustering.cluster import KMeans
from queryLog import normalize
import numpy as np
import Pycluster as clust
		
