import os
import re
import pypdf

def read_pdf(file_path):
    pdf_reader = pypdf.PdfReader(file_path)
    
    text_content = []
    
    # Iterate through all the pages and extract text
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text_content.append(page.extract_text() + '\n##PAGE##\n')
    
    return ''.join(text_content)

def write_text_to_file(text, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def get_items(text):
    anchor = 'Itens do Pedido'
    text = text.replace(anchor, '\n' + anchor)
    items = [] 
    for line in text.split('\n'):
        if anchor in line:
            item = line[len(anchor):].strip()
            item = re.sub(r'Sku.*?Quantidade: ', '\tQ:', item)
            item = item.replace('Valor Unitário:', '\tV:')
            item = re.sub(r'Valor Total:.*', ';', item)

            items.append(item)
    
    return items



def main():
    p1 = 'Lojadafrateschi-pedidos1a2.pdf'
    p2 = 'Lojadafrateschi-pedidos3a22.pdf'
    p3 = 'Lojadafrateschi-pedidos23a24.pdf'
    input_pdf_path = '/Users/luciano/Dropbox/0-FJR/frateschi/material-rodante/' + p3
    
    directory, file_name = os.path.split(input_pdf_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    
    output_text_path = os.path.join(directory, f"{file_name_without_ext}.txt")
    
    # Read the PDF and extract text
    text = read_pdf(input_pdf_path)

    items = get_items(text)
    
    # Write the extracted text to a file
    write_text_to_file('\n'.join(items), output_text_path)
    
    print(f"Purchase orders have been written to {output_text_path}")

if __name__ == "__main__":
    main()