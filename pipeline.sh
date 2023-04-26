echo "======================================================================"
echo "Scraping dataset starting 7 days ago"
echo "======================================================================"
lastweek=$(date -d '-8 days' '+%Y-%m-%d')
python scrape_weekly.py --scrapedate=${lastweek}

echo "======================================================================"
echo "Staring creating csv from database"
echo "======================================================================"
currdate=$(date '+%Y-%m-%d')
currdate=$(date -d '-1 days' '+%Y-%m-%d')
python create_csv_from_db.py --currdate=${currdate}

echo "======================================================================"
echo "Starting inference"
echo "======================================================================"
python inference.py \
--threshold 0.85 \
--model_path model/model_v0.pt \
--load_input_file articles_all_${currdate}.csv \
--save_name news_labelled_${currdate}

echo "======================================================================"
echo "Starting inference for events"
echo "======================================================================"
python inference_events.py \
--data_path news_labelled_${currdate}_shortlist.csv \
--currdate=${currdate}

echo "======================================================================"
echo "Starting inference for infra model"
echo "======================================================================"
python inference_infra.py \
--model_path model100.pt \
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
python keyword_csv_gen.py \
--filename news_labelled_${currdate}_shortlist.csv --num_articles 5 \
--currdate=${currdate}

# echo "======================================================================"
# echo "Process Parivesh articles"
# echo "======================================================================"
# python process_parivesh_articles.py --currdate=${currdate}

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
mv news_labelled_${currdate}_shortlist.json ${foldername}
mv event_clusters_${currdate}.csv ${foldername}
mv event_clusters_${currdate}.xlsx ${foldername}
mv keywords_${currdate}.csv ${foldername}
mv keywords_${currdate}.xlsx ${foldername}

echo "======================================================================"
echo "Tweeting articles"
echo "======================================================================"
python tweet_articles.py --currdate=${currdate}