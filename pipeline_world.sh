echo "======================================================================"
echo "Scraping dataset starting 7 days ago"
echo "===============9======================================================"
lastweek=$(date -d '-7 days' '+%Y-%m-%d')
python scrape_weekly_world.py --scrapedate=${lastweek}

echo "======================================================================"
echo "Staring creating csv from database"
echo "======================================================================"
currdate=$(date '+%Y-%m-%d')
#currdate=$(date -d '-1 days' '+%Y-%m-%d')
python create_csv_from_db_world.py --currdate=${currdate}

echo "======================================================================"
echo "Starting inference"
echo "======================================================================"
python inference.py \
--threshold 0.85 \
--model_path results/full_train/lr1e-05/batch_size4/dropout0.2/fc2dim768/pos_weight3/model_v0.pt \
--load_input_file articles_all_world_${currdate}.csv --world \
--save_name news_labelled_${currdate}
# --model_path results/models/lr5e-06/batch_size4/dropout0.2/fc2dim768/pos_weight3/model.pt \

echo "======================================================================"
echo "Starting inference for infra model"
echo "======================================================================"
python inference_infra.py \
--model_path model100.pt \
--load_input_file news_labelled_${currdate}_world_shortlist.csv

echo "======================================================================"
echo "Cleaning up files"
echo "======================================================================"
foldername="weekly-news/news_${currdate}"
mkdir -p ./$foldername/world/
mv articles_all_world_$currdate.csv ${foldername}/world
mv news_labelled_${currdate}_world_masterlist.csv ${foldername}/world
mv news_labelled_${currdate}_world_masterlist.xlsx ${foldername}/world
# mv news_labelled_${currdate}_world_masterlist.json ${foldername}/world
mv news_labelled_${currdate}_world_shortlist.csv ${foldername}/world
mv news_labelled_${currdate}_world_shortlist.xlsx ${foldername}/world
# mv news_labelled_${currdate}_world_shortlist.json ${foldername}/world
