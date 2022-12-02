import requests
import newspaper

# ARTICLES_TO_DOWNLOAD = \
#     ["https://www.thestatesman.com/cities/live-pangolin-rescued-one-arrested-2-1503064250.html",
#     "https://timesofindia.indiatimes.com/city/hyderabad/ivory-jewellery-sale-on-facebook-busted-2-held-in-hyderabad/articleshow/93416973.cms",
#     "https://timesofindia.indiatimes.com/city/kolkata/500-endangered-turtles-rescued-in-kolkata/articleshow/91925914.cms",
#     "https://timesofindia.indiatimes.com/city/kolkata/illegal-coral-traders-aides-hold-officials-captive-two-arrested/articleshow/91386832.cms",
#     "https://timesofindia.indiatimes.com/city/kolkata/coral-dealer-arrested-from-chiria-more/articleshow/91298007.cms",
#     "https://timesofindia.indiatimes.com/city/kolkata/2-arrested-for-keeping-live-corals-in-fish-tanks/articleshow/91272867.cms",
#     "https://timesofindia.indiatimes.com/city/ludhiana/leopard-skins-seized-tibba-man-arrested/articleshow/91111504.cms",
#     "https://timesofindia.indiatimes.com/city/bhopal/leopard-claws-pangolin-scales-seized-in-bastar/articleshow/89553382.cms",
#     "https://timesofindia.indiatimes.com/city/mumbai/mumbai-three-held-for-trying-to-sell-red-sand-boas-for-occult-practices/articleshow/87311632.cms",
#     "https://timesofindia.indiatimes.com/city/jaipur/police-stumble-upon-wildlife-traffickers-2-held-with-antlers-gun/articleshow/91824836.cms"]

ARTICLES_TO_DOWNLOAD = ["https://indianexpress.com/article/cities/mumbai/mumbai-over-29000-mongoose-hair-paint-brushes-seized-15-held-6088589/"]

for i, url in enumerate(ARTICLES_TO_DOWNLOAD):
    article = newspaper.Article(url)
    article.download()
    article.parse()

    try:
        file_name = article.authors[0].replace(" ", "_") + article.publish_date.strftime("_%m_%d_%Y")
    except Exception:
        file_name = "TITLE_NA_" + str(i)

    file_name = "output_text/" + file_name + ".txt"
    
    with open(file_name, "w") as text_file:
        text_file.write("[TITLE]\n" + article.title + "\n\n")
        text_file.write("[BODY]\n" + article.text)