<div align="center">
<h1 align="center">
<img src="./assets/icon.ico" width="100" />
<br>Cresliant</h1>
<h3>A powerful node-based image editor made in Python</h3>
<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/License-GPL--3.0-orange.svg" alt="License" />
</p>
</div>

---

## 📖 Table of Contents
- [📖 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [📦 Features](#-features)
- [🚀 Getting Started](#-getting-started)
- [🤝 Contributing](#-contributing)
---


## 📍 Overview

Cresliant is a powerful node-based image editor made in Python. It offers an easy way to manipulate and enhance images through a user-friendly interface. With Cresliant, users can take advantage of a wide range of features and functionalities, all powered by Python's extensive libraries for image processing.

---

## 📦 Features

### Node-Based Editing
- Cresliant's node-based editing system provides a visual and intuitive way to create complex image manipulations. Users can connect different nodes to build custom image processing pipelines, making it easy to experiment with various effects and transformations.

### Real-Time Preview
- The real-time preview feature allows users to see the effects of their edits instantly. This helps streamline the editing process, as users can make adjustments and fine-tune their work in real-time without the need for time-consuming rendering.

### Comprehensive Node List
- Cresliant has a comprehensive node list, showcasing an extensive collection of pre-built nodes that cover a wide range of image editing tasks. This includes nodes for basic operations like cropping and resizing, advanced filters for artistic effects, and utility nodes for managing data flow within the editing graph.

### Plugin Support (Not Yet Implemented)
- Cresliant boasts a dynamic plugin architecture, allowing users to extend their already broad range of processing nodes. The plugin system empowers the community to contribute and enhance the editor's capabilities.

---

## 🚀 Getting Started

### 🔧 Installation

You can either use one of the precompiled executables provided in the [releases](https://github.com/Cresliant/Cresliant/releases) or install and run locally:
<br/><br/>

1. Clone the Cresliant repository:
```sh
git clone https://github.com/Cresliant/Cresliant
```

2. Change to the project directory:
```sh
cd Cresliant
```

3. Install the dependencies using poetry:
```sh
pip install poetry
poetry install --no-root
```

### 🤖 Running Cresliant

```sh
poetry run python main.py
```

---

## 🤝 Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/Cresliant/Cresliant/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/Cresliant/Cresliant/discussions)**: Share your insights, provide feedback, or ask questions.
- **[Report Issues](https://github.com/Cresliant/Cresliant/issues)**: Submit bugs found or log feature requests for Cresliant.

#### *Contributing Guidelines*

<details closed>
<summary>Click to expand</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone <your-forked-repo-url>
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Install Pre-commit Hooks**: So you don't forget to run them.
   ```sh
   poetry run pre-commit install
   ```
5. **Make Your Changes**: Develop and test your changes locally.
6. **Commit Your Changes**: Commit with a clear and concise message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
7. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
8. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.

</details>

---
