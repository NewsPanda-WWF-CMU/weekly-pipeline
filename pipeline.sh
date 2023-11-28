#! /bin/bash

day_lag=${1:-0}
week_lag=$((7+$day_lag))
lastweek=$(date -d '-'${week_lag}' days' '+%Y-%m-%d')
currdate=$(date -d '-'${day_lag}' days' '+%Y-%m-%d')

echo "======================================================================"
echo "Downloading files from Parivesh website"
echo "======================================================================"
python src/parivesh_combine_csv.py --currdate=${currdate}

echo "======================================================================"
echo "Scraping dataset starting 7 days ago"
echo "======================================================================"
python src/scrape_weekly.py --scrapedate=${lastweek}

echo "======================================================================"
echo "Staring creating csv from database"
echo "======================================================================"
python src/create_csv_from_db.py --currdate=${currdate}

echo "======================================================================"
echo "Starting inference"
echo "======================================================================"
python src/inference.py \
--threshold 0.85 \
--model_path model/model_v0.pt \
--load_input_file articles_all_${currdate}.csv \
--save_name news_labelled_${currdate}

echo "======================================================================"
echo "Starting inference for events"
echo "======================================================================"
python src/inference_events.py \
--data_path news_labelled_${currdate}_shortlist.csv \
--currdate=${currdate}

echo "======================================================================"
echo "Starting inference for infra model"
echo "======================================================================"
python src/inference_infra.py \
--model_path model/model_infra.pt \
--load_input_file news_labelled_${currdate}_shortlist.csv

# echo "======================================================================"
# echo "Creating JSON"
# echo "======================================================================"
# python json_creator.py \
# --filename news_labelled_${currdate}_shortlist.csv \
# --currdate=${currdate}

echo "======================================================================"
echo "Creating keywords file"
echo "======================================================================"
python src/keyword_csv_gen.py \
--filename news_labelled_${currdate}_shortlist.csv --num_articles 5 \
--currdate=${currdate}

echo "======================================================================"
echo "Process Parivesh articles"
echo "======================================================================"
python src/parivesh_process.py --currdate=${currdate}

echo "======================================================================"
echo "Cleaning up files"
echo "======================================================================"
foldername="weekly-news/news_${currdate}"
mkdir -p ./$foldername/
mv articles_all_$currdate.csv $foldername
mv news_labelled_${currdate}_masterlist.csv ${foldername}
mv news_labelled_${currdate}_masterlist.xlsx ${foldername}
mv news_labelled_${currdate}_shortlist.csv ${foldername}
mv news_labelled_${currdate}_shortlist.xlsx ${foldername}
# mv news_labelled_${currdate}_shortlist.json ${foldername}
mv event_clusters_${currdate}.csv ${foldername}
mv event_clusters_${currdate}.xlsx ${foldername}
mv keywords_${currdate}.csv ${foldername}
mv keywords_${currdate}.xlsx ${foldername}
mv parivesh_${currdate}.csv ${foldername}

echo "======================================================================"
echo "Tweeting articles"
echo "======================================================================"
python src/tweet_articles.py --currdate=${currdate}

echo "======================================================================"
echo "Uploading to Google Drive"
echo "======================================================================"
python src/google_drive_uploader.py --currdate=${currdate}