import fitz as fz # PyMuPdf
import json
import re


def pdf_get_titles(file):
    file_tocs = file.get_toc()
    
    for i in range(len(file_tocs) - 1, 0, -1):
        if file_tocs[i-1][0] == file_tocs[i][0] == 1:
            del file_tocs[i-1]
        
        # Удалить из списка заголовков подзаголовки без нумерации
        if not re.match(r"^\d+\.\d+", file_tocs[i][1]) and file_tocs[i][0] != 1:
            del file_tocs[i]
        
    
    return file_tocs


def create_tocs_dict(file_tocs_list):
    tocs_dict = {}
    chapter_num = 0
    section_num = 0
    subsection_num = 0
    
    for id, el in enumerate(file_tocs_list):
        lvl, title, _ = el
        if lvl == 1:
            chapter_num += 1
            section_num = 0
            tocs_dict[str(chapter_num)] = {'title': title, 'sections': {}}
        
        elif lvl == 2:
            if re.match(r"^\d+\.\d+", title):
                section_num += 1
                subsection_num = 0
                sec_title =  title.split(' ', 1)
                tocs_dict[str(chapter_num)]['sections'].update(
                    {f"{sec_title[0]}": {'title': sec_title[1], 'text': f"get_text(id)", 'subsections': {}}}
                )
        
        elif lvl == 3:
            subsection_num += 1
            
            if re.match(r"^\d+\.\d+\.\d+", title):
                subsec_title =  title.split(' ', 1)
                tocs_dict[str(chapter_num)]['sections'][sec_title[0]] \
                    ['subsections'][subsec_title[0]] = {'title': subsec_title[1], 'text': f"get_text(id)"}
    
    return tocs_dict


def get_text(id):
    lvl = file_titles[id][0]
    title = file_titles[id][1]
    page = file_titles[id][2]
    text = (file.load_page(page - 1)).get_text()
    
    # print(text)


if __name__ == '__main__':
    file_dir = "./File.pdf"
    
    with fz.open(file_dir) as file:
        file_titles = pdf_get_titles(file)
        tocs_dict = create_tocs_dict(file_titles)
        get_text(0)
    
    with open('out.txt', 'w+', encoding='utf-8') as f:
        for el in file_titles:
            print(el, file=f)
    
    with open('./structure.json', 'w+', encoding='utf-8') as f:
        json.dump(tocs_dict, f, ensure_ascii=False, indent=4)
