# Contributing Guidelines

## Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies updates
- `ci`: CI/CD related changes
- `perf`: Performance improvements

### Scopes
- `deps`: Dependencies
- `core`: Core functionality
- `ocr`: OCR related changes
- `pdf`: PDF processing
- `nlp`: Natural Language Processing
- `ml`: Machine Learning
- `ui`: User Interface
- `test`: Testing related

### Examples
```
feat(ocr): add new image preprocessing filter
fix(pdf): correct page rotation calculation
chore(deps): update project dependencies
docs: update installation instructions
```


Perfecto. Aquí tienes una instrucción completamente integrada y clara para tu agente, en inglés, incluyendo la ejecución del git add . && git commit -m "..." y respetando tus reglas de convención de commits:

⸻

Agent Activation Instruction – Auto Commit Behavior

Upon activation, the agent must automatically:
	1.	Review all uncommitted changes in the working directory.
	2.	Stage all modified files using:

git add .


	3.	Generate a detailed commit message that:
	•	Is written entirely in English.
	•	Follows the Conventional Commits specification:

<type>(<scope>): <description>

[optional body]

[optional footer]


	•	Includes the correct commit type and scope as defined below.
	•	Clearly summarizes what was changed and why.
	•	If multiple logical changes exist, either:
	•	Group them coherently in a single message, or
	•	Create multiple commits with appropriate separation.

	4.	Execute the commit using:

git commit -m "<generated commit message>"


Commit Message Convention

We follow the Conventional Commits format:

Types:
	•	feat: New feature
	•	fix: Bug fix
	•	docs: Documentation changes
	•	style: Code style (formatting, missing semicolons, etc.)
	•	refactor: Code refactoring
	•	test: Adding or updating tests
	•	chore: Maintenance tasks, dependency updates
	•	ci: CI/CD related changes
	•	perf: Performance improvements

Scopes:
	•	deps: Dependencies
	•	core: Core functionality
	•	ocr: OCR related changes
	•	pdf: PDF processing
	•	nlp: Natural Language Processing
	•	ml: Machine Learning
	•	ui: User Interface
	•	test: Testing related

Examples:

feat(ocr): add new image preprocessing filter
fix(pdf): correct page rotation calculation
chore(deps): update project dependencies
docs: update installation instructions