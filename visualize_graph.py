import os
import subprocess
import argparse
from git import Repo
import sys

def get_commit_history(repo_path, filename):
    repo = Repo(repo_path)
    commits = list(repo.iter_commits())
    relevant_commits = []

    for commit in commits:
        if filename in commit.stats.files:
            relevant_commits.append(commit)

    return relevant_commits

def build_graph(commits):
    graph_data = "digraph G {\n"
    commit_pairs = []

    for commit in commits:
        for parent in commit.parents:
            commit_pairs.append((parent.hexsha, commit.hexsha))

    for parent_commit, child_commit in commit_pairs:
        graph_data += f'  "{parent_commit}" -> "{child_commit}";\n'

    graph_data += "}\n"
    return graph_data

def save_graph_to_file(graph_data, output_path, graph_visualizer_path):
    with open('graph.dot', 'w') as dot_file:
        dot_file.write(graph_data)

    try:
        subprocess.run([graph_visualizer_path, '-Tpng', 'graph.dot', '-o', output_path], check=True)
    except subprocess.CalledProcessError:
        print("Ошибка при создании изображения графа.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей коммитов.")
    parser.add_argument('--graph-visualizer-path', required=True, help="Путь к программе для визуализации графов.")
    parser.add_argument('--repo-path', required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument('--output-path', required=True, help="Путь к файлу для сохранения графа зависимостей.")
    parser.add_argument('--filename', required=True, help="Имя файла для поиска коммитов.")

    args = parser.parse_args()

    if not os.path.isdir(args.repo_path):
        print("Указанный путь к репозиторию не существует.")
        sys.exit(1)

    commits = get_commit_history(args.repo_path, args.filename)
    if not commits:
        print("Нет коммитов, содержащих указанный файл.")
        sys.exit(1)

    graph_data = build_graph(commits)
    save_graph_to_file(graph_data, args.output_path, args.graph_visualizer_path)

    print("Граф зависимостей успешно создан и сохранен в", args.output_path)

if __name__ == "__main__":
    main()
