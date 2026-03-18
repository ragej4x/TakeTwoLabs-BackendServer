from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'api' / 'main.py'
text = p.read_text(encoding='utf-8')
new_text = text.replace('numberOfPairs=row.numberOfPairs,', 'numberOfPairs=(row.numberOfPairs or 1),')
if new_text == text:
    print('No replacements needed')
else:
    p.write_text(new_text, encoding='utf-8')
    print('Replacements applied')
