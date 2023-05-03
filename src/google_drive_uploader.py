import os
import argparse
import yaml
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


# https://stackoverflow.com/questions/66107562/create-new-folder-on-gdrive-using-pydrive-module
class Google_Drive:
	def __init__(self, folder_id):
		self.gauth = GoogleAuth()
		self.gauth.LocalWebserverAuth()
		self.drive = GoogleDrive(self.gauth)
		self.folder_id = folder_id

	def create_folder_if_not_exist(self, folder_name):
		self.file_list = self.drive.ListFile({'q': "trashed=false"}).GetList()
		titles = [i['title'] for i in self.file_list]
		if folder_name in titles:
			for i in self.file_list:
				if i['title']==folder_name: 
					return i['id'] 
		file_metadata = {
			'title': folder_name,
			'parents': [{'id': self.folder_id}], #parent folder
			'mimeType': 'application/vnd.google-apps.folder'
		}
		folder = self.drive.CreateFile(file_metadata)
		folder.Upload()
		folder_id = folder['id']
		return folder_id

	def upload_files(self, file_list, parent_folder_id):
		if type(file_list) != type([]):
			file_list = [file_list]
		for f in file_list:
			gfile = self.drive.CreateFile({'parents': [{'id': parent_folder_id}]})
			# Read file and set it as the content of this instance.
			gfile.SetContentFile(f)
			gfile.Upload() # Upload the file.
			print(f"{f} uploaded to Google drive.")

	def delete_files(self, id_list):
		if type(id_list) != type([]):
			id_list = [id_list]
		for f in id_list:
			gfile = self.drive.CreateFile({'id': f})
			gfile.Delete()
			print(f"{f} deleted.")

def run(config):
	with open(config.wwf_id_yaml) as f:
		a = yaml.load(f)
		wwf_folder_id = a['gdrive_id']
	gdrive = Google_Drive(wwf_folder_id)
	currdate_folder = gdrive.create_folder_if_not_exist(config.currdate)

	file_list = []
	weekly_news_folder = f"weekly-news/news_{config.currdate}"
	file_list.append(f"{weekly_news_folder}/news_labelled_{config.currdate}_masterlist.xlsx")
	file_list.append(f"{weekly_news_folder}/news_labelled_{config.currdate}_shortlist.xlsx")
	if f"event_clusters_{config.currdate}.xlsx" in os.listdir(weekly_news_folder):
		file_list.append(f"{weekly_news_folder}/event_clusters_{config.currdate}.xlsx")
	file_list.append(f"{weekly_news_folder}/keywords_{config.currdate}.xlsx")		
	file_list.append(f"{weekly_news_folder}/parivesh_{config.currdate}.csv")

	gdrive.upload_files(file_list, currdate_folder)


if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--currdate', type=str, default=None)
	parser.add_argument('--wwf_id_yaml', type=str, default='database.yaml')
	config = parser.parse_args()
	run(config)
	