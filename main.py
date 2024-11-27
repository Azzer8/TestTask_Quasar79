import fitz as fz # PyMuPdf
import json
import re


def pdf_get_toc(file):
    file_toc_list = file.get_toc()
    
    for i in range(len(file_toc_list)-1, 0, -1):
        # Удалить из списка заголовков повторяющиеся 
        # обозначения глав и разделы введения/предисловия
        if ((file_toc_list[i][0] == file_toc_list[i-1][0] == 1) and
            (file_toc_list[i][2] == file_toc_list[i-1][2])) or \
        ((file_toc_list[i][0] == file_toc_list[i-1][0] == 1) and
         ((file_toc_list[i][2] - file_toc_list[i-1][2])) < 4
        ):
            del file_toc_list[i-1]
        
        # Удалить из списка заголовков подзаголовки без нумерации
        if not re.match(r"^\d+\.+", file_toc_list[i][1]) and file_toc_list[i][0] != 1:
            del file_toc_list[i]
        
    return file_toc_list


def create_toc_dict(file_toc_list):
    file_toc_dict = {}
    chapter_num = 0
    
    for id, el in enumerate(file_toc_list):
        lvl, title, _ = el
        if lvl == 1:
            chapter_num += 1
            file_toc_dict[str(chapter_num)] = {'title': title, 'sections': {}}
            if file_toc_list[id + 1][0] == 1:
                file_toc_dict[str(chapter_num)] = {'text': f"{get_text(id)}"}
        
        elif lvl == 2:
            if re.match(r"^\d+\.\d+", title):
                sec_title =  title.split(' ', 1)
                file_toc_dict[str(chapter_num)]['sections'].update(
                    {f"{sec_title[0]}": {'title': sec_title[1], 
                                                'text': f"{get_text(id)}", 
                                                'subsections': {}}
                    }
                )
        
        elif lvl == 3:
            if re.match(r"^\d+\.\d+\.\d+", title):
                subsec_title =  title.split(' ', 1)
                file_toc_dict[str(chapter_num)]['sections'][sec_title[0]] \
                    ['subsections'][subsec_title[0]] = {'title': subsec_title[1], 
                                                                        'text': f"{get_text(id)}"}
    
    return file_toc_dict


def get_text(id):
    cur_lvl = file_toc_list[id][0]
    next_lvl = file_toc_list[id + 1][0] if id + 1 < len(file_toc_list) else None

    if re.match(r"^\d+\.+", cur_title := file_toc_list[id][1]):
        cur_title = cur_title.split(' ', 1)
    else:
        cur_title = [file_toc_list[id][1]]
    
    if re.match(r"^\d+\.+", \
        next_title := file_toc_list[id+1][1] if id + 1 < len(file_toc_list) else ''
    ):
        next_title = next_title.split(' ', 1)
    else:
        next_title = [file_toc_list[id+1][1]] if id + 1 < len(file_toc_list) else ['']

    cur_page = file_toc_list[id][2]
    next_page = file_toc_list[id + 1][2] if id + 1 < len(file_toc_list) else file.page_count
    # Если уже нет заголовков читаем до последней страницы 
    # (в будущем улучшить, т.к. может быть раздел "Источники" и т.д.)
    
    page_text_list = []
    
    for i in range(cur_page, next_page if next_lvl == 1 else next_page + 1):
        cur_page_text = (file.load_page(i - 1)).get_text().replace(' \n', ' ').strip()
        # Если нет следующего заголовка или текст не начинается со следующего заголовка
        # добавляем страницу в список считанных страниц
        if next_title[0] == '' or not re.match(rf"^{next_title[0].lower()}", cur_page_text.lower()):
            page_text_list.append(cur_page_text)

    text = '\n'.join(page_text_list)
    
    # Ищем индекс текущего заголовка в тексте страницы 
    # и прибавляем его длину к найденному индексу
    text_start_idx = text.lower().find(f"{cur_title[0].lower()}") \
                            + len(' '.join(cur_title) if len(cur_title) != 1 else cur_title[0])
    
    # Ищем индекс следующего заголовка в тексте страницы
    # Если следующего заголовка нет, берем длину текста страницы
    text_end_idx = text.lower().rfind(f"{next_title[0].lower()}") \
                                                    if next_title[0] else len(text)
    
    if text_end_idx != -1:
        text = text[text_start_idx:text_end_idx].strip()
    else:
        text = text[text_start_idx:].strip()
        
    return text


if __name__ == '__main__':
    FILE_DIR = "./File.pdf"
    
    try:
        with fz.open(FILE_DIR) as file:
            file_toc_list = pdf_get_toc(file)
            file_toc_dict = create_toc_dict(file_toc_list)
    except fz.FileNotFoundError:
        print(f"Файл не найден: {FILE_DIR}")
        exit()
    except fz.FileDataError:
        print(f"Некорректный файл: {FILE_DIR}")
        exit()
    
    # with open('file_toc_list.txt', 'w+', encoding='utf-8') as f:
    #     for el in file_toc_list:
    #         print(el, file=f)
    
    with open('./structure.json', 'w+', encoding='utf-8') as f:
        json.dump(file_toc_dict, f, ensure_ascii=False, indent=4)
