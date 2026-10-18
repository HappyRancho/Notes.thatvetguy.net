from html import escape
import re
BASE="https://notes.thatvetguy.net"
ICONS = {
    'home': '<path d="m3 10 9-8 9 8v11h-6v-7H9v7H3Z"/>',
    'chevron': '<path d="m9 5 7 7-7 7"/>',
    'cap': '<path d="m2 8 10-5 10 5-10 5Z"/><path d="M5 10v7c4 4 10 4 14 0v-7M22 8v8"/>',
    'bone': '<path d="M7 3a3 3 0 0 0-4 4c-2 2 0 6 3 5l6 6c-1 3 3 5 5 3a3 3 0 0 0 4-4c2-2 0-6-3-5l-6-6c1-3-3-5-5-3Z"/>',
    'heart': '<path d="M20.8 4.6c-2-2-6-2-8.8 1-2.8-3-6.8-3-8.8-1-3.6 3.9 1 9.6 8.8 16 7.8-6.4 12.4-12.1 8.8-16Z"/><path d="M3 11h4l2-4 4 9 2-5h6"/>',
    'leaf': '<path d="M12 22V11M12 18C4 18 2 12 3 5c7 1 10 5 9 13Zm1-2c0-7 4-11 9-12 1 8-2 12-9 12ZM7 9l5 9m5-10-4 8"/>',
    'flask': '<path d="M8 2h8M9 2v7L3 19q-1 3 3 3h12q4 0 3-3L15 9V2M7 14h10"/>',
    'microbe': '<ellipse cx="12" cy="12" rx="7" ry="8"/><path d="M12 1v3m0 16v3M3 5l3 3m12 8 3 3M1 12h4m14 0h4M3 19l3-3M18 8l3-3M9 10h1m4 5h1m-1-7h1m-5 8h1"/>',
    'microscope': '<path d="m10 2 5 3-5 9-5-3Z"/><path d="M14 10a6 6 0 0 1 1 11H6m-3 1h17M4 16h8"/>',
    'dna': '<path d="M6 2c0 10 12 10 12 20M18 2C18 12 6 12 6 22M7 5h10M9 9h6m-6 6h6m-8 4h10"/>',
    'shield': '<path d="m12 2 9 4v6c0 5-4 8-9 10-5-2-9-5-9-10V6Z"/><path d="M8 12h8m-4-4v8"/>',
    'milk': '<path d="M8 2h8v4l3 4v12H5V10l3-4Zm-3 9h14M8 6h8"/>',
    'stethoscope': '<path d="M4 2v6a5 5 0 0 0 10 0V2M9 13v3a5 5 0 0 0 10 0v-2M3 2h3m6 0h3"/><circle cx="19" cy="11" r="3"/>',
    'target': '<circle cx="11" cy="13" r="9"/><circle cx="11" cy="13" r="5"/><path d="m11 13 9-10m-3 1 1-3 2 2 3 1-3 2-3-2Z"/>',
    'bulb': '<path d="M8 17c0-3-4-5-4-9a8 8 0 0 1 16 0c0 4-4 6-4 9Zm0 3h8m-7 3h6M9 9l3 3 3-3m-3 3v5"/>',
    'brain': '<path d="M12 4c-3-4-7-1-6 2-4-1-6 4-3 6-3 3 0 7 3 6 0 4 5 5 6 1 1 4 6 3 6-1 3 1 6-3 3-6 3-2 1-7-3-6 1-3-3-6-6-2Zm0 0v15M6 6l2 3-2 2m0 7 2-3m10-9-2 3 2 2m0 7-2-3"/>',
    'chart': '<path d="M4 21v-6h3v6Zm7 0V9h3v12Zm7 0V3h3v18Z"/>',
    'calculator': '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M7 5h10v4H7Zm0 8h3m4 0h3m-10 4h3m4 0h3M8.5 11.5v3m7 1v3"/>',
    'chain': '<path d="m10 7 3-3a5 5 0 0 1 7 7l-3 3m-3 3-3 3a5 5 0 0 1-7-7l3-3m1 6 8-8"/>',
    'map': '<path d="m2 6 7-3 7 3 6-3v16l-6 3-7-3-7 3ZM9 3v16m7-13v16"/><path d="M12 2a3 3 0 0 1 6 0c0 2-3 6-3 6s-3-4-3-6Z"/>',
    'people': '<circle cx="12" cy="5" r="4"/><path d="M5 22v-4a7 7 0 0 1 14 0v4ZM3 9a3 3 0 1 0 0 6m18-6a3 3 0 1 1 0 6M3 17c-2 0-2 3-2 5h2m18-5c2 0 2 3 2 5h-2"/>',
    'megaphone': '<path d="m3 10 11-3 6-4v17l-6-4-11-2Zm3 5 2 7h4l-2-6M14 7v9m9-9v6"/>',
    'message': '<path d="M3 18a9 9 0 1 1 5 3l-6 2Zm4-9h10M7 14h7"/>',
    'sliders': '<path d="M2 6h5m5 0h10M2 18h10m5 0h5"/><circle cx="9.5" cy="6" r="2.5"/><circle cx="14.5" cy="18" r="2.5"/>',
    'arrow': '<path d="M4 12h15m-6-6 6 6-6 6"/>',
    'external': '<path d="M7 17 17 7M7 7h10v10"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
    'menu': '<path d="M4 5h16M4 12h16M4 19h16"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
    'book': '<path d="M3 5c4-1 6-1 9 1 3-2 5-2 9-1v15c-4-1-6-1-9 1-3-2-5-2-9-1Z"/><path d="M12 6v15"/>',
    'paper': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    'check': '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="m8 12 3 3 5-6"/>',
    'cross': '<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6Z"/>',
    'pill': '<path d="m9 4 11 11a4.95 4.95 0 0 1-7 7L2 11a4.95 4.95 0 0 1 7-7ZM7 16l8-8"/>',
    'spark': '<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z"/>',
    'phone': '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10 18h4"/>',
    'tools': '<path d="m14 6 4-4 4 4-4 4M14 6l-3 3M3 21l8-8M5 3l16 16-2 2L3 5Z"/>',
    'paw': '<path d="M7 13c-4 4-3 8 1 7l4-1 4 1c4 1 5-3 1-7-3-4-7-4-10 0Z"/><ellipse cx="5" cy="8" rx="2" ry="3"/><ellipse cx="10" cy="5" rx="2" ry="3"/><ellipse cx="16" cy="5" rx="2" ry="3"/><ellipse cx="21" cy="9" rx="2" ry="3"/>',
}

def icon(name, cls=''):
    if name == 'telegram':
        return f'<svg class="icon-svg {cls}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.6 3.2c.4-.2.9.2.8.7l-3.3 16c-.1.7-.6.8-1.1.5l-5.1-3.8-2.5 2.4c-.3.3-.6.5-1 .5l.4-5.3 9.6-8.7c.4-.4-.1-.6-.5-.3L7 12.6l-5-1.6c-.6-.2-.6-.6.1-.9Z"/></svg>'
    return f'<svg class="icon-svg {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def link(url, text, cls='', external=False):
    external = url.startswith(('https://','http://')) and not url.startswith(BASE+'/')
    extra = ' target="_blank" rel="noopener noreferrer"' if external else ''
    if external and icon('external') not in text:
        text=text.replace(icon('arrow'),icon('external')) if icon('arrow') in text else text+icon('external')
    return f'<a href="{escape(url, quote=True)}" class="{cls}"{extra}>{text}</a>'

