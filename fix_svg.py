import re

with open('backend/logo_vec.svg', 'r', encoding='utf-8') as f:
    data = f.read()

# Replace classes with inline fills
data = data.replace('class="cls-1"', 'fill="none"')
data = data.replace('class="cls-2"', 'fill="#23b574"')
data = data.replace('class="cls-3"', 'fill="#0f8fef"')

# Remove <defs> for better FPDF support
data = re.sub(r'<defs>.*?</defs>', '', data, flags=re.DOTALL)

with open('backend/logo_vec.svg', 'w', encoding='utf-8') as f:
    f.write(data)

print("SVG modificado con atributos inline")
