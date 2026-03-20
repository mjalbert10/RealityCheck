import kagglehub

# Download latest version
path = kagglehub.dataset_download("vinayaks0n1/imdb-tv-show-reviews")
KAGGLE_API_TOKEN="KGAT_6d4c8319beca6a499bdb261ad40c77f9"
print("Path to dataset files:", path)