## Setup

	pip install -r requirements.txt

## Build docs

	pydoc -w incremental_oversizing_model
	open incremental_oversizing_model_3.html

## Theory

- If you were going to build a PV project
- Different approaches to modeling PV project.
- Given declining costs of PV resources and increasing population
- It may be economically viable to build all of PV plant at the beginning
- Or it may be better to build the PV plant in stages.
- Here we have the following predefined inputs based on academic data references at the end:

- Compound annual demand growth - The energy demand year on year cumulatively summed.
- PV cost reductions year on year - Balance of system (BOS) cost reductions
- Discount rate - discount future costs of PV supplies
- Initial daily demand - demand at year 0 of the community for energy
- Base costs - costs for PV modules and BOS at year 0
- Operation and maintenance costs - costs at year 0
- Fixed rebuild costs - overhead costs for labour, time, analysis per rebuild of PV plant
- Project lifetime - how long the project will last

- Outputs:

- Net present cost - Some of all costs over lifetime
- Total discounted energy - total energy production
- Levelized costs of electricity - uniform cost agnostic of underlying energy source over lifetime of project

- Given that you can choose to reanalyze and rebuild the plant once, twice, N times over a projects lifetime. We calculate the cheapest number of rebuilds. Opmtize for cheapest number of rebuilds.


## Welcome to GitHub Pages

You can use the [editor on GitHub](https://github.com/hamishbeath/off-grid-energy/edit/master/README.md) to maintain and preview the content for your website in Markdown files.

Whenever you commit to this repository, GitHub Pages will run [Jekyll](https://jekyllrb.com/) to rebuild the pages in your site, from the content in your Markdown files.

### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/hamishbeath/off-grid-energy/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
