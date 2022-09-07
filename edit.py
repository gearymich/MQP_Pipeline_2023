
with open("countries.txt", "r") as f:
    countries = []
    for country in f:
        if country != '\n':
            country = country.strip()
            if len(country) > 1:
                countries.append(country.lower())
len(countries)

with open("countries.txt", "w") as f:
    for country in countries:
        f.write(country + '\n')
