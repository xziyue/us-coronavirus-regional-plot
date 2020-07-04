from scrape_n_parse import CoronavirusInfo
import pickle

with open('states_data.bin', 'rb') as infile:
    data = pickle.load(infile)

print('loaded local data')