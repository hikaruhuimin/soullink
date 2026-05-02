content = open('templates/divination/home.html', 'rb').read().decode('utf-8', 'ignore')

# Replace universe_bg with milky_way and add movement animation
content = content.replace('url("/static/images/universe_bg.jpg")', 'url("/static/images/milky_way.jpg")')

# Add galaxy rotation/movement animation keyframes if not exists
if 'galaxyDrift' not in content:
    # Find the hero CSS and add animation
    content = content.replace(
        'min-height: 300px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n}',
        'min-height: 350px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    background-size: 150% auto;\n    animation: galaxyDrift 60s ease-in-out infinite alternate;\n}'
    )
    
    # Also update the other hero definition if it exists
    content = content.replace(
        'min-height: 300px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    border: 1px solid rgba(139, 92, 246, 0.2);\n}',
        'min-height: 350px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    border: 1px solid rgba(139, 92, 246, 0.2);\n    background-size: 150% auto;\n    animation: galaxyDrift 60s ease-in-out infinite alternate;\n}'
    )
    
    # Add the keyframes animation before </style> or after existing keyframes
    galaxy_keyframes = '''
@keyframes galaxyDrift {
    0% { background-position: 0% 30%; }
    25% { background-position: 50% 20%; }
    50% { background-position: 100% 40%; }
    75% { background-position: 60% 60%; }
    100% { background-position: 20% 30%; }
}

@keyframes galaxyRotate {
    0% { transform: scale(1) rotate(0deg); }
    50% { transform: scale(1.1) rotate(1deg); }
    100% { transform: scale(1) rotate(0deg); }
}
'''
    # Insert before the closing </style> tag
    content = content.replace('</style>', galaxy_keyframes + '</style>', 1)

# Also make the hero-decoration (stars on top) move with the galaxy
content = content.replace(
    '.hero-decoration {\n    position: absolute;\n    top: 20px;\n    left: 0; right: 0;',
    '.hero-decoration {\n    position: absolute;\n    top: 20px;\n    left: 0; right: 0;\n    animation: galaxyRotate 60s ease-in-out infinite;'
)

open('templates/divination/home.html', 'wb').write(content.encode('utf-8'))
print('done')
