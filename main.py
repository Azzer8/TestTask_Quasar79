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
            if file_tocs_list[id + 1][0] == 1:
                tocs_dict[str(chapter_num)] = {'text': f"{get_text(id)}"}
        
        elif lvl == 2:
            if re.match(r"^\d+\.\d+", title):
                section_num += 1
                subsection_num = 0
                sec_title =  title.split(' ', 1)
                tocs_dict[str(chapter_num)]['sections'].update(
                    {f"{sec_title[0]}": {'title': sec_title[1], 'text': f"{get_text(id)}", 'subsections': {}}}
                )
        
        elif lvl == 3:
            subsection_num += 1
            
            if re.match(r"^\d+\.\d+\.\d+", title):
                subsec_title =  title.split(' ', 1)
                tocs_dict[str(chapter_num)]['sections'][sec_title[0]] \
                    ['subsections'][subsec_title[0]] = {'title': subsec_title[1], 'text': f"{get_text(id)}"}
    
    return tocs_dict


def get_text(id):
    next_lvl = file_titles[id + 1][0] if id + 1 < len(file_titles) else None
    cur_title = file_titles[id][1].split(' ', 1)
    next_title = file_titles[id + 1][1].split(' ', 1) if id + 1 < len(file_titles) else None
    cur_page = file_titles[id][2]
    # Если уже нет заголовков читаем до последней страницы 
    # (в будущем улучшить, т.к. может быть раздел "Источники" и т.д.)
    next_page = file_titles[id + 1][2] if id + 1 < len(file_titles) else file.page_count
    text = ""
    
    for i in range(cur_page, next_page if next_lvl == 1 else next_page + 1):
        temp_text = (file.load_page(i - 1)).get_text()
        text += temp_text.strip()
    
    text_start_idx = text.find(f"{cur_title[0]}") + 1 + len(' '.join(cur_title))
    text_end_idx = text.rfind(f"{next_title[0]}") if next_title else len(text)
    text = text[text_start_idx:text_end_idx].strip()
    
    # with open('text.txt', 'a+', encoding='utf-8') as f:
    #     print(f"{cur_title[0]}:", file=f)
    #     print(text, file=f)
    #     print("-"*100, file=f)
    #     print(file=f)
        
    return text


if __name__ == '__main__':
    file_dir = "./File.pdf"
    
    with fz.open(file_dir) as file:
        file_titles = pdf_get_titles(file)
        tocs_dict = create_tocs_dict(file_titles)
    
    # with open('out.txt', 'w+', encoding='utf-8') as f:
    #     for el in file_titles:
    #         print(el, file=f)
    
    with open('./structure.json', 'w+', encoding='utf-8') as f:
        json.dump(tocs_dict, f, ensure_ascii=False, indent=4)
