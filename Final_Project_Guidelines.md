# CSS142P Final Project Requirements and Guidelines

## 1 Project Overview
The project requires each project team to design, implement, analyze, and present a simulation study that addresses a real decision problem. The result must support a recommendation with reproducible evidence.
* Define a meaningful decision problem.
* Construct an appropriate conceptual and computational model.
* Design reproducible simulation experiments.
* Analyze results, variability, and uncertainty.
* Present an evidence-based recommendation and explain the model's limitations.

## 2 Course Outcomes

| Outcome | Evidence in the Project |
| :--- | :--- |
| CO1 | Design and implement a simulation model using an appropriate tool or programming language. |
| CO2 | Analyze and interpret simulation results to support a decision. |
| CO3 | Apply simulation techniques to a real problem in engineering, computer science, or management. |

## 3 Topic and Decision Question
Choose a real system or decision problem that can be studied within the Week 7 to Week 10 timeline. The project must answer one clear decision question. A project that only describes or visualizes data without conducting simulation experiments does not meet the requirement.

**Example decision question:** How will adding one service counter affect average waiting time, queue length, and staff utilization during peak hours?

### Acceptable Project Domains
* Queuing and service systems
* Computer networks and cloud services
* Manufacturing and operations
* Inventory and supply chain management
* Healthcare operations
* Finance and risk analysis
* AI system capacity or performance
* Transportation, traffic, energy, or resource allocation
* Another domain approved by the instructor

## 4 Project Scope
Keep the study focused enough to complete and verify within four course weeks. Each project team must use the following limits:
* One primary decision question
* One main simulation method
* One baseline scenario and at least two alternative scenarios
* At least two measurable performance indicators
* At least 30 independent replications per stochastic scenario, or a justified convergence-based alternative
* One sensitivity analysis

## 5 Required Project Components

### Problem Framing
* Identify the problem, decision-maker, system boundary, assumptions, and performance indicators.
* State one decision question that the simulation experiments will answer.

### Conceptual Model
* Provide a diagram, flowchart, process map, state model, or equivalent representation.
* Show the system components, inputs, outputs, relationships, and sources of randomness.

### Input Data and Assumptions
* Use public data, properly anonymized collected data, published parameters, or documented synthetic data.
* Explain each important value or probability distribution and identify its source.
* Do not include confidential, personally identifiable, or restricted information.

### Simulation Method and Implementation
* Use Monte Carlo, discrete-event, continuous, queuing, or another justified simulation method.
* Python and Google Colab are recommended. Another tool requires instructor approval.
* The model must run without unresolved errors, use readable names, expose key parameters, and produce the reported measures.

### Verification and Validation
* Provide at least two documented checks showing that the model works as intended and behaves reasonably.
* Check calculations, event logic, simple or extreme cases, and consistency with assumptions or available evidence.

### Experiment Design
* Compare the baseline with at least two alternatives using the same performance measures.
* Document random seeds, replications, scenario conditions, and all controlled variables.

### Results and Analysis
* Use readable tables and graphs to compare scenarios.
* Report means, variability, and a 95 percent confidence interval where applicable.
* Include one sensitivity analysis and explain what the results mean for the decision-maker.

### Recommendation and Limitations
* Answer the decision question directly and support the recommendation with numerical evidence.
* Explain when the recommendation applies, the model's limitations, and possible improvements.

## 6 Required Deliverables
Submit one ZIP file containing all final materials.
1. Final report in PDF format
2. Executable model as an IPYNB, PY, or approved simulation-tool file
3. Input data files when applicable
4. Generated result tables or CSV files
5. Final presentation in PPTX or PDF format
6. README file with instructions for reproducing the results

**Required filename:** `CSS142P_FinalProject_TeamNumber_ProjectTitle.zip`

**Recommended Folder Structure:**
CSS142P FinalProject TeamNumber ProjectTitle/
    README.txt
    Report/CSS142P_FinalProject_Report.pdf
    Model/CSS142P FinalProject.ipynb
    Data/
    Results/
    Presentation/CSS142P_FinalProject Presentation.pptx

## 7 Final Report Structure
1. Executive Summary
2. Problem and Decision Question
3. System Boundary and Conceptual Model
4. Input Data and Assumptions
5. Simulation Method and Implementation
6. Verification and Validation
7. Experiment Design
8. Results and Uncertainty Analysis
9. Recommendation and Limitations
10. References
11. Appendices when needed

Use one recognized citation style consistently. Credit all external data, code, models, images, and ideas.

## 8 Presentation and Demonstration
Each project team will present during Week 10. The project team has 10 minutes for the presentation and demonstration, followed by up to 5 minutes for questions. There is no required number of slides. Use only the slides needed to communicate the study clearly.
* Problem and decision question
* Conceptual model, inputs, and assumptions
* Simulation method and experiment design
* Verification and validation evidence
* Results, uncertainty, and sensitivity analysis
* Recommendation and limitations
* Working demonstration or reproducible execution of the model

## 9 Project Timeline

| Week | Checkpoint | Required Evidence |
| :--- | :--- | :--- |
| 7 | Topic proposal | Team members, project title, decision question, scope, and conceptual model |
| 8 | Model plan | Input assumptions, selected method, baseline, alternatives, and experiment plan |
| 9 | Working model | Executable model, verification checks, and preliminary results |
| 10 | Final submission | Complete ZIP package, presentation, demonstration, and responses to questions |

## 10 Grading Rubric

| Criterion | Performance Evidence | Points |
| :--- | :--- | :--- |
| Problem framing | Clear decision question, stakeholder, scope, system boundary, conceptual model, and performance measures | 15 |
| Model construction | Appropriate method, justified inputs and assumptions, correct executable implementation, and readable documentation | 25 |
| Experiment design | Baseline and alternatives, controlled conditions, seeds, replications, scenario logic, and reproducibility | 20 |
| Analysis | Verification, validation, accurate results, uncertainty, confidence intervals where applicable, sensitivity analysis, recommendation, and limitations | 25 |
| Communication | Complete report, effective visuals, organized presentation, working demonstration, responses to questions, and proper citations | 15 |
| **Total** | | **100** |

A model that cannot be executed cannot earn full credit for model construction, experiment design, or reproduced analysis.

## 11 Sample Project Outlines
These examples show an appropriate project scope. Project teams must develop their own model, justify their inputs, and document their own results. The numbers below illustrate an experiment design and do not prescribe a required topic.

### Sample Monte Carlo Help Desk Capacity

| Project element | Illustrative example |
| :--- | :--- |
| Decision question | How many help desk analysts are needed to keep the probability that daily ticket workload exceeds staff capacity below 10 percent? |
| Method | Monte Carlo simulation |
| Inputs | Daily ticket count, ticket handling time, and productive minutes per analyst. Cite each source or label the values as synthetic. |
| Scenarios | Baseline with three analysts, Alternative A with four analysts, and Alternative B with five analysts. |
| Performance measures | Probability of daily overload and average unused or shortage minutes. |
| Experiment | Use the same seed list for fair comparison and run at least 30 independent replications per scenario. A project team may use 1,000 simulated days when computing time remains reasonable. |
| Verification and validation | Check one fixed-input case by hand. Test zero-demand and unusually highdemand -cases. Confirm that adding capacity does not increase overload under identical inputs. |
| Sensitivity analysis | Increase average daily ticket demand by 15 percent and repeat the scenario comparison. |
| Expected conclusion | Recommend the smallest staffing level that meets the overload target. Report the numerical evidence, uncertainty, tradeoff, and model limitations. |

**Reporting example:** For each scenario, report the mean, variability, and a 95 percent confidence interval where appropriate. State whether the scenario meets the decision target and explain the result in words.

### Additional Sample Questions
* **Inventory:** Which reorder point minimizes expected total cost while keeping stockout probability below 5 percent?
* **Server capacity:** How many virtual machine instances are needed to keep overload probability below 2 percent as request volume varies?
* **Maintenance:** Which preventive maintenance interval reduces average downtime without creating excessive maintenance work?
* **Service system:** How will adding one service counter affect waiting time, queue length, and staff utilization during peak hours?

Project teams may adapt an example after changing the system context and supporting all assumptions with relevant evidence. The final submission must contain the project team's experiment results and a recommendation based on those results.

## 12 Final Submission Checklist
- [ ] The project answers one clear decision question.
- [ ] The conceptual and computational models agree.
- [ ] The notebook or program runs from beginning to end.
- [ ] Random seeds, replications, and experiment settings are documented.
- [ ] The baseline and at least two alternatives are included.
- [ ] At least two verification or validation checks are documented.
- [ ] Results include uncertainty and sensitivity analysis.
- [ ] The recommendation uses numerical evidence.
- [ ] The report explains important limitations.
- [ ] The ZIP includes the report, model, data, results, presentation, and README.
- [ ] The filename follows the required format.
- [ ] The correct ZIP file is attached and submitted in Blackboard.