# AIAntiPlagiatForDock

## Для чего?
Ищет текст, сгенерированный ИИ, в папке с документами формата .doc(x)

### Начало
Рекомендовано работать в контейнере, но не обязательно. 
Запускаем скрипт сборки и настройки окружения.
Зависимости ставятся в вирутальные переменные.

``` 

docker build . -t AIAntiPlagiatForDock
<-----------> ЖДЕМ МИНУТ 30 <----------->
```
После успешной сборки запускаем контейнер

```
docker run -it AIAntiPlagiatForDock /bin/bash
source venv/bin/activate
```

После этого рядом с приглашением ввода оболочки должно появится ` venv `

```
(venv) root#
```

Теперь можно использовать скрипты. 

Самый важный скрипт - **checkAIGenerateText.py**.

Ему передается целевая папка ` target_dir `, где лежат файлы формата .doc(x), которые нужно проверить.

В качестве примера дана тестовая папка target. 

Пример запуска

```
python checkAIGenerateText.py -roberta_base -roberta_large -classificator -words -entropy -referat --output_json test.json --output_exel test.xlsx target   >> test.log 
```

На выходе три файла:
1. test.json  -  файл со всеми значениями в json формате, удобно конвертировать в тиблицу, например;

2. test.xlsx - таблица с результатами;

3. test.log - log с подробностями работы программы.









# ВСЕ ДАЛЕЕ - ИСПРАВИТЬ:

Также через опцию ` -o ` указываем название файла, куда будут писаться логи.

Два необязательных, но важных аргумента, которыми выбираем, какой моделью будут проверяться документы.
* ` -gpt2 `           - https://openai-openai-detector.hf.space/ 

* ` -classificator `  - https://platform.openai.com/ai-text-classifier

*В процессе работы исходные документы будут делиться на куски по 300 (gpt2) - 800 (классификатор) слов и последовательно загружаться на системы.*
*Немного может влиять на точность*

Для использования рекомендована **classificator**, поскольку выше точность и скрость. 

``` !!!Для её использования нужно получить ключ авторизации от open.ai и изменить переменную  bearer_token (строка 16) ```

Как это сделать смотррите тут
https://github.com/promptslab/openai-detector

Пример запуска
```
python checkAIGenerateText.py -gpt2 -classificator -o out.txt target_dir/
```
Такой запуск будет содержать ошибки о неудачных попытках отправки данных на сайт. 
Если хотите их избежать или перенаправить в файл, используйте поток ошибок

Пример запуска
```
python checkAIGenerateText.py -gpt2 -classificator -o out.txt target_dir/ 2> /dev/null
```

## От автора

### Пример вывода программы
```

   Name: diplom.docx 
---------------------------------------------------------------------------- 
 ----- ChatGPT 2.0 ----- 
 File: 0, Fake probability: 86.6% 
File: 1, Fake probability: 98.6% 
File: 2, Fake probability: 99.6% 
File: 3, Fake probability: 97.9% 
File: 4, Fake probability: 98.8% 
File: 5, Fake probability: 78.7% 
File: 6, Fake probability: 96.3% 
File: 7, Fake probability: 97.6% 
File: 8, Fake probability: 91.1% 
File: 9, Fake probability: 93.7% 

 ---> avg_fake_probability: 94.0 	 not_loaded_files: 0 
----- AI Text Classifier ----- 
 Pprobability: 85.61134299461072 
 Class: unlikely 
 Pprobability: 98.28689412532744 
 Class: possibly 
 Pprobability: 96.86604367264252 
 Class: unclear if it is 
 Pprobability: 98.52267847361583 
 Class: possibly 
 Pprobability: 98.92245327954687 
 Class: possibly 
 Pprobability: 98.54683594431548 
 Class: possibly 
 Pprobability: 97.3247073920071 
 Class: unclear if it is 
 Pprobability: 99.35944841471745 
 Class: likely 
 
 ---> Average fake probability: 96.7%
 ---> AI GENERATE!

```

Ввиду ограничений в работе веб сайтов весть файл скормить им не получается. 
Приходится делить на небольшие куски и загружать отдельно. 
Поэтому для каждого такого "куска" выводится отдельная статистика, а в конце считается среднее по всем кусочкам.

Итак, в логах сначала выводится имя файла, который был обработан.
Далее идет вывод режимов работы:


Сначала `ChatGPT2` - у него низкая точность и долгое время работы из-за не очень хорошего сайта.
Ее вывод такой:
 ``` File: 0, Fake probability: 96.5% ```
Где  ` File `  - номер кусочка файла, а ` Fake probability `:  - вероятность того, что текст сгенерирован. Эти значения даны в процентах, чем больше, тем хуже.

После загрузки всех кусков файла, программа делает подсчет среднего значения по всем файлам -  ` avg_fake_probability: 92.7% ` 
Также есть отладочная информация в виде переменной ` not_loaded_files: ` - в ней написано сколько кусочков не удалось загрузить. Этот параметр влияет на точность

Далее идет  вывод ` AI Text Classifier `
Для кусочков документа у него два параметра:
 ` Pprobability: 9.039683710252689 `  - это вероятность того, что текст сгенерирован.  Значения даны, как СЫРЫЕ ДАННЫЕ. Больше - хуже.
Вторая переменная самая интересная: ` Class:  ` - это  классификация полученных данных. 

Видимо классификатор по значению и каким-то своим параметрам приравнивает значения к определенному классу. 

Классы, которые мне попадались:

``` very unlikely (50>),  unlikely(50-88), unclear if it is(97<), possibly(98<), likely  (99<) ```
Приоритетной информацией является именно параметр классификации. 

Далее считается среднее значение ``` ---> Average fake probability: 18.2% ``` 

Если это значение превышает порог 75, то появляется предупреждение о **ВОЗМОЖНОЙ ГЕНЕРАЦИИ ТЕКСТА ИИ**

Выглядит так: ```  AI generation possible ```

Если это значение превышает порог 96, то оно **ОДНОЗНАЧНО СГЕНЕРИРОВАНО ИИ**

Предупреждение выглядит так: ``` ---> AI GENERATE! ``` 

Скорее всего придется смотреть на текст разбитый по кусочкам. Значение должно "гулять" в процессе. 
Основной ориентир, конечно, классификатор.
