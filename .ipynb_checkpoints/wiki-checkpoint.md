```sh
mkdir wiki
cd wiki
curl https://dumps.wikimedia.org/ptwiki/latest/ptwiki-latest-pages-articles-multistream-index.txt.bz2 --create-dirs -o data/ptwiki-latest-pages-articles-multistream-index.txt.bz2
curl https://dumps.wikimedia.org/ptwiki/latest/ptwiki-latest-pages-articles-multistream.xml.bz2 --create-dirs -o data/ptwiki-latest-pages-articles-multistream.xml.bz2
git clone https://github.com/attardi/wikiextractor.git
cd ./wikiextractor
pip install -e .
cd ../../data
python3 -m wikiextractor.WikiExtractor ptwiki-latest-pages-articles-multistream-index.txt.bz2 
python3 -m wikiextractor.WikiExtractor ptwiki-latest-pages-articles-multistream.xml.bz2 
```