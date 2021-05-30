from google.cloud import vision
import io
import sys
import os
import config
import ocr2record

def ocr(image_file_name):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/satoyoshiharu/hmc-dialog-server/hmc-dialog-97e55e12dbdf.json"
    client = vision.ImageAnnotatorClient()
    with io.open(config.WORKING_DIR + 'record/' + image_file_name + '.jpg', 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image,image_context={"language_hints":["ja"]})
    text = ''
    with open(config.WORKING_DIR + image_file_name + '.txt', 'w') as text_file:
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                print(f'\nBlock confidence: {block.confidence}\n')
                text_file.write(f'\nBlock confidence: {block.confidence}\n')

                for paragraph in block.paragraphs:
                    print(f'Paragraph confidence: {paragraph.confidence}')
                    text_file.write(f'Paragraph confidence: {paragraph.confidence}')

                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        text += word_text
                        print(f'Word text: {word_text} (confidence: {word.confidence})')
                        text_file.write(f'Word text: {word_text} (confidence: {word.confidence})')

                        for symbol in word.symbols:
                            print(f'\tSymbol: {symbol.text} (confidence: {symbol.confidence})')
                            text_file.write(f'\tSymbol: {symbol.text} (confidence: {symbol.confidence})')
    if text != '':
        ocr2record.ocr2record(text)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(response.error.message))

if __name__ == '__main__':
    args = sys.argv
    ocr(args[1])