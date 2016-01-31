
'''
Statistics
'''

# Description: Calculate type distribution of each journal
# Input: parsed json data: origin.json
# Output: stat_type.csv
# Return:
def stat_type(input_path=output_path+parsed_file, output_path=output_path+'stat_type.csv'):
	cate_papers = dict()
	with open(input_path, "r") as fi:
		cate_papers = json.loads(fi.read())
	type_list = list()
	cate_journal_type_distri = dict()
	with open(output_path, "w") as fo:
		for cate, cate_dict in cate_papers.items():
			cate_journal_type_distri[cate] = dict()
			# fo.write(cate+'\n')
			for journal, articles in sorted(cate_dict.items()):
				cate_journal_type_distri[cate][journal] = dict()
				type_dict = dict()
				# fo.write(journal+'\n')
				for article in articles:
					type_dict[article['type']] = type_dict.get(article['type'], 0)+1
				for type_str, count in sorted(type_dict.items()):
					if type_str not in type_list:
						type_list.append(type_str)
					cate_journal_type_distri[cate][journal][type_str] = count
					# fo.write(","+type_str+','+str(count)+'\n')
			# fo.write('\n')
		type_list = sorted(type_list)
		for type_str in type_list:
			fo.write(","+type_str)
		fo.write("\n")
		for cate, cate_dict in sorted(cate_journal_type_distri.items()):
			for journal, type_distri in sorted(cate_dict.items()):
				fo.write(journal)
				for type_str in type_list:
					fo.write(","+str(type_distri.get(type_str, 0)))
				fo.write("\n")

