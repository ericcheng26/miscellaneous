
'''
========================
    使用方法
========================
# path: <dir_path>/<file_name>.json
# static_dir_path: <dir_path>/<static_dir>
# discussion_path: <dir_path>/<static_dir>/discussion.html
1. 建立物件
  parser = Vet_yamol_parser(yamol_raw_html_string, path)

2. 執行分析並回傳路徑
  result_path = parser()
========================
    執行邏輯
========================
分析的過程會把資料存下來
分成 json, 圖檔, discussion.html
後兩者會放在 static 的資料夾
'''

from os.path import isabs, isfile, isdir, basename, dirname, join
from os import makedirs
from json import load, dump
from bs4 import BeautifulSoup as BS
import requests
import re


class Vet_yamol_parser():
    # 初始化，用於存取 raw data 與 建立 DOM
    def __init__(self, html, path):
        self.html = html
        self.path = path

        self.dom = BS(html, 'lxml')
        self.domlist = self.dom.select('[class="col-lg-12 reponse-card"]')

        self.static_dir = join(dirname(path), 'static')

        self.discussion_path = join(self.static_dir, 'discussion.html')

        # 建立 json 檔的佔存容器
        self.container = {}

    # 萃取所求資料，並序列化

    def __call__(self):
        # domlist loop
        for bstag in self.domlist:

            # 取得題目與選項
            qid, question, choices = self._get_choice_question(bstag)

            # 取得答案
            ans = self._get_ans(bstag)

            # 儲存圖片並回傳路徑
            img_path_list = self._img_extract(bstag, qid, self.static_dir)

            # 儲存詳解討論
            self._extract_discussion(bstag, qid, self.discussion_path)

            # 打包成字典
            result = self._todict(qid, question, choices, ans, img_path_list)

            self.container.update(result)

        self.result_path = self._serialize(self.container, self.path)
        return self.result_path

#############################以下為內部方法的實作##########################################

    def _get_choice_question(self, bstag):
        itemcontent = bstag.select('[class="itemcontent"]')
        text = itemcontent[0].getText().replace('\n', ' ')

        if '重新載圖' in text:
            question, temp_choices = text[text.find(
                '重新載圖')+4:text.find('(A)')].strip(), text[text.find('(A)'):].strip()
        else:
            question, temp_choices = text[:text.find(
                '(A)')].strip(), text[text.find('(A)'):].strip()

        choices = []
        for c in ['(B)', '(C)', '(D)']:
            i = temp_choices.find(c)
            choices.append(temp_choices[:i].strip())
            temp_choices = temp_choices[i:]
        choices.append(temp_choices)
        qid = question[:question.find('.')]
        return qid, question, choices

    def _get_ans(self, bstag):
        answer = bstag.select('[class="col-sm-6 col-md-4 col-lg-4"]')
        text = answer[0].getText()
        ans = text[text.find('答案：')+3]
        return ans

    def _img_save(self, url, path):

        if (not isdir(dirname(path))) and (dirname(path) != ''):
            makedirs(dirname(path))

        response = requests.get(url)
        file = open(path, "wb")
        file.write(response.content)
        file.close()
        return path

    def _img_extract(self, bstag, qid, static_path):
        content = bstag.select('[class="itemcontent"]')
        imglist = content[0].select('img')
        if imglist == []:
            return None
        else:
            img_path_list = []
            for i, img in enumerate(imglist):
                img_src = img['src']
                path = join(static_path, qid + '_' + str(i) + '.jpg')
                img_path = self._img_save(img_src, path)
                img_path_list.append(img_path)
            return img_path_list

    def _todict(self, number, question, choices, answer, image_path=None, solution=None, ):

        if isinstance(number, int) or isinstance(number, float):
            number = str(int(number))

        if number != question[:question.find('.')]:
            raise ValueError('Wrong question number!')

        if len(choices) != 4:
            try:
                raise Warning(f'There are {len(choices)} choice(s), not 4!')
            except Warning as w:
                print('Warning: %s' % w)

        if not any([answer in choice[:3] for choice in choices]):
            print(number)
            print(choices)
            try:
                raise ValueError('No such answer!')
            except ValueError as e:
                print(e)

        result = {number: [question, choices, answer]}

        if image_path != None:
            result[number].append(image_path)
        return result

    def _serialize(self, container: dict, path: str):

        if not isinstance(container, dict):
            raise TypeError('The 1st arg. must be a dictionary.')

        if isfile(path):
            with open(path, 'r') as f:
                data = load(f)
        else:
            if (not isdir(dirname(path))) and (dirname(path) != ''):
                makedirs(dirname(path))
            data = {}

        data.update(container)

        with open(path, 'w') as f:
            dump(data, f, ensure_ascii=False)
        if dirname(path) != '':
            print(f'已建立 {basename(path)} 於 {dirname(path)}')
            return [basename(path), dirname(path)]
        else:
            print(f'已建立 {path} 於當前工作資料夾')
            return path

    def _extract_discussion(self, bstag, qid, doc_path):

        if (not isdir(dirname(doc_path))) and (dirname(doc_path) != ''):
            makedirs(dirname(doc_path))

        img_size_control = r'''
        <style type="text/css">
          img{max-width:80%; height: auto;}
        </style>
    '''
        re_pattern = r'<span class="comment">(.*)<a href="support_open.php'
        addition_filter = r'<label class="badge badge-danger">已解鎖</label>'
        div_open = r'<div style="border: 2px solid red; border-radius: 5px; border-color: gray; padding: 25px 25px 25px 25px; margin-top: 25px;width: 1000px;">'

        discussion_list = bstag.select(
            '[class="well itemcomment"] div[style*="min-height"]')

        with open(doc_path, 'a') as f:
            f.write(img_size_control)

        for i, e in enumerate(discussion_list):
            re_result = re.search(re_pattern, str(e), re.DOTALL)
            target = re_result.group(1).replace(addition_filter, '')

            result = div_open + f'<h1>{qid}-{i+1}</h1>' + target + '</div>'*2

            with open(doc_path, 'a') as f:
                f.write(result)
