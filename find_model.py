import os

found = False
for root, dirs, files in os.walk('venv/Lib/site-packages/mediapipe'):
    if 'hand_landmarker.task' in files:
        model_path = os.path.join(root, 'hand_landmarker.task')
        print(f'Found model at: {model_path}')
        found = True
        break

if not found:
    print('Model file not found in MediaPipe installation')
    print(f'Searching for .task files...')
    for root, dirs, files in os.walk('venv/Lib/site-packages/mediapipe'):
        task_files = [f for f in files if f.endswith('.task')]
        if task_files:
            print(f'Found .task files in {root}: {task_files}')
