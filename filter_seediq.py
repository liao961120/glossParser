#%%
import json

def main():
    # Read all data
    with open("all_lang-long-text.json") as f:
        glosses = json.load(f)

    with open("all_lang-long-text-glossary.json") as f:
        glossary = json.load(f)

    # Filter
    seediq_glosses = filter_glosses(glosses, "賽德克")
    seediq_glossary = filter_glossary(glossary, "Seediq")

    # Save results
    with open("seediq-long-text.json", "w") as f:
        json.dump(seediq_glosses, f, ensure_ascii=False)
    with open("seediq-long-text-glossary.json", "w") as f:
        json.dump(seediq_glossary, f, ensure_ascii=False)


def filter_glosses(glosses, key='賽德克'):
    return [ g for g in glosses if key in g['meta']['language'] ]


def filter_glossary(glossary, key='Seediq'):
    filtered_glossary = []

    for g in glossary:
        new_sense = {}
        for sense, locations in g[1].items():
            seediq_loc = [ l for l in locations if l.startswith('Seediq') ]
            if len(seediq_loc) > 0:
                new_sense[sense] = seediq_loc
        if len(new_sense) > 0:
            g[1] = new_sense
            filtered_glossary.append(g)
        
    return filtered_glossary
            

#%%
if __name__ == "__main__":
    main()