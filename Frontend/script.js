const analyzeButton = document.getElementById("analyzeButton");

const results = document.getElementById("results");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");


// ============================================================
// HELPER FUNCTIONS
// ============================================================

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}


function hideError() {
    errorBox.textContent = "";
    errorBox.classList.add("hidden");
}


function clearElement(element) {
    element.innerHTML = "";
}


function createListItem(text, className = "") {
    const item = document.createElement("div");

    if (className) {
        item.className = className;
    }

    item.textContent = text;

    return item;
}


// ============================================================
// ANALYZE BUTTON
// ============================================================

analyzeButton.addEventListener("click", async function () {

    hideError();

    const url =
        document.getElementById("url").value.trim();

    const degree =
        document.getElementById("degree").value.trim();

    const year =
        document.getElementById("year").value.trim();

    const cgpa =
        document.getElementById("cgpa").value.trim();

    const skills =
        document.getElementById("skills").value.trim();


    // --------------------------------------------------------
    // VALIDATION
    // --------------------------------------------------------

    if (!url) {
        showError("Please enter an opportunity URL.");
        return;
    }


    try {

        new URL(url);

    } catch {

        showError(
            "Please enter a valid opportunity URL."
        );

        return;
    }


    // --------------------------------------------------------
    // LOADING STATE
    // --------------------------------------------------------

    analyzeButton.disabled = true;
    analyzeButton.textContent = "ANALYZING...";

    loading.classList.remove("hidden");

    results.classList.add("hidden");


    try {

        console.log("Sending request to NAVIGATE backend...");


        // ----------------------------------------------------
        // BACKEND REQUEST
        // ----------------------------------------------------

        const response = await fetch(
            "https://navigate-bwxd.onrender.com/analyze",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    url: url,
                    degree: degree,
                    year: year,
                    cgpa: cgpa,
                    skills: skills
                })
            }
        );


        console.log(
            "Backend HTTP status:",
            response.status
        );


        // ----------------------------------------------------
        // READ RESPONSE
        // ----------------------------------------------------

        const data = await response.json();

        console.log(
            "NAVIGATE backend response:",
            data
        );


        // ----------------------------------------------------
        // BACKEND ERROR
        // ----------------------------------------------------

        if (!response.ok || data.status === "error") {

            throw new Error(
                data.message ||
                `Backend returned HTTP ${response.status}`
            );
        }


        // ----------------------------------------------------
        // EXTRACT BACKEND DATA
        // ----------------------------------------------------

        const student =
            data.student_profile || {};

        const opportunity =
            data.opportunity || {};

        const requirements =
            opportunity.requirements || {};

        const eligibility =
            data.eligibility || {};

        const actionPlan =
            data.action_plan || {};


        // ====================================================
        // OPPORTUNITY
        // ====================================================

        document.getElementById(
            "opportunityTitle"
        ).textContent =
            requirements.title ||
            "Opportunity";


        document.getElementById(
            "organization"
        ).textContent =
            requirements.organization ||
            "Organization not specified";


        document.getElementById(
            "opportunityType"
        ).textContent =
            requirements.type ||
            "Not specified";


        document.getElementById(
            "location"
        ).textContent =
            requirements.location ||
            "Not specified";


        document.getElementById(
            "deadline"
        ).textContent =
            requirements.deadline ||
            "Not specified";


        document.getElementById(
            "minimumCgpa"
        ).textContent =
            requirements.minimum_cgpa ||
            "Not specified";


        // ====================================================
        // STATUS
        // ====================================================

        const statusElement =
            document.getElementById("status");


        const overallStatus =
            eligibility.overall_status ||
            "NEEDS REVIEW";


        statusElement.textContent =
            overallStatus;


        statusElement.className =
            "status";


        if (overallStatus === "ELIGIBLE") {

            statusElement.classList.add(
                "eligible"
            );

        } else if (
            overallStatus === "NOT ELIGIBLE"
        ) {

            statusElement.classList.add(
                "not-eligible"
            );

        } else {

            statusElement.classList.add(
                "review"
            );
        }


        // ====================================================
        // OFFICIAL REQUIREMENTS
        // ====================================================

        const requirementsList =
            document.getElementById(
                "requirementsList"
            );


        clearElement(requirementsList);


        const officialRequirements = [];


        // Degree

        if (
            requirements.required_degree &&
            requirements.required_degree.length
        ) {

            requirements.required_degree.forEach(
                requirement => {

                    officialRequirements.push(
                        "Degree: " + requirement
                    );

                }
            );
        }


        // Year

        if (
            requirements.required_year &&
            requirements.required_year.length
        ) {

            requirements.required_year.forEach(
                requirement => {

                    officialRequirements.push(
                        "Academic year: " + requirement
                    );

                }
            );
        }


        // CGPA

        if (requirements.minimum_cgpa) {

            officialRequirements.push(
                "Minimum CGPA: " +
                requirements.minimum_cgpa
            );
        }


        // Skills

        if (
            requirements.required_skills &&
            requirements.required_skills.length
        ) {

            officialRequirements.push(
                "Required skills: " +
                requirements.required_skills.join(", ")
            );
        }


        // Other requirements

        if (
            requirements.other_requirements &&
            requirements.other_requirements.length
        ) {

            requirements.other_requirements.forEach(
                requirement => {

                    officialRequirements.push(
                        requirement
                    );

                }
            );
        }


        if (officialRequirements.length === 0) {

            requirementsList.appendChild(
                createListItem(
                    "No explicit requirements were extracted.",
                    "requirement"
                )
            );

        } else {

            officialRequirements.forEach(
                requirement => {

                    requirementsList.appendChild(
                        createListItem(
                            requirement,
                            "requirement"
                        )
                    );

                }
            );
        }


        // ====================================================
        // MATCH SCORE
        // ====================================================

        document.getElementById(
            "matchScore"
        ).textContent =
            eligibility.match_score ??
            "—";


        // ====================================================
        // ELIGIBILITY CHECKS
        // ====================================================

        const eligibilityList =
            document.getElementById(
                "eligibilityList"
            );


        clearElement(eligibilityList);


        if (
            eligibility.checks &&
            eligibility.checks.length
        ) {

            eligibility.checks.forEach(
                check => {

                    const item =
                        document.createElement("div");


                    const normalizedStatus =
                        String(
                            check.status || ""
                        )
                        .toLowerCase()
                        .replaceAll(" ", "-");


                    item.className =
                        "eligibility-item " +
                        normalizedStatus;


                    const status =
                        document.createElement("div");


                    status.className =
                        "eligibility-status";


                    status.textContent =
                        check.status ||
                        "UNKNOWN";


                    const requirement =
                        document.createElement("strong");


                    requirement.textContent =
                        check.requirement ||
                        "Requirement";


                    const reason =
                        document.createElement("div");


                    reason.className =
                        "eligibility-reason";


                    reason.textContent =
                        check.reason ||
                        "No explanation provided.";


                    item.appendChild(status);

                    item.appendChild(
                        requirement
                    );

                    item.appendChild(reason);


                    eligibilityList.appendChild(
                        item
                    );

                }
            );

        } else {

            eligibilityList.appendChild(
                createListItem(
                    "No eligibility checks available.",
                    "eligibility-item"
                )
            );
        }


        // ====================================================
        // GAPS
        // ====================================================

        const missingList =
            document.getElementById(
                "missingList"
            );


        clearElement(missingList);


        const criticalGaps =
            eligibility.critical_gaps || [];


        const needsInput =
            eligibility.needs_input || [];


        if (
            criticalGaps.length === 0 &&
            needsInput.length === 0
        ) {

            missingList.appendChild(
                createListItem(
                    "No missing information identified.",
                    "gap"
                )
            );

        } else {

            criticalGaps.forEach(
                gap => {

                    missingList.appendChild(
                        createListItem(
                            "BLOCKER: " + gap,
                            "gap"
                        )
                    );

                }
            );


            needsInput.forEach(
                input => {

                    missingList.appendChild(
                        createListItem(
                            "NEEDS INPUT: " + input,
                            "gap"
                        )
                    );

                }
            );
        }


        // ====================================================
        // CURRENT POSITION
        // ====================================================

        document.getElementById(
            "currentPosition"
        ).textContent =
            actionPlan.current_position ||
            `Student profile: ${student.degree || "Degree not provided"}, ` +
            `Year ${student.year || "?"}, ` +
            `CGPA ${student.cgpa || "?"}.`;


        // ====================================================
        // ACTION PLAN
        // ====================================================

        const actionPlanElement =
            document.getElementById(
                "actionPlan"
            );


        clearElement(actionPlanElement);


        if (
            actionPlan.action_plan &&
            actionPlan.action_plan.length
        ) {

            actionPlan.action_plan.forEach(
                step => {

                    const item =
                        document.createElement("div");


                    item.className =
                        "action-step";


                    const number =
                        document.createElement("div");


                    number.className =
                        "step-number";


                    number.textContent =
                        step.step || "";


                    const content =
                        document.createElement("div");


                    const action =
                        document.createElement("div");


                    action.className =
                        "step-action";


                    action.textContent =
                        step.action ||
                        "Action";


                    const why =
                        document.createElement("div");


                    why.className =
                        "step-why";


                    why.textContent =
                        step.why ||
                        "";


                    content.appendChild(action);

                    content.appendChild(why);


                    item.appendChild(number);

                    item.appendChild(content);


                    actionPlanElement.appendChild(item);

                }
            );

        } else {

            actionPlanElement.appendChild(
                createListItem(
                    "No action plan available.",
                    "action-step"
                )
            );
        }


        // ====================================================
        // SKILLS
        // ====================================================

        const skillsList =
            document.getElementById(
                "skillsList"
            );


        clearElement(skillsList);


        if (
            actionPlan.skills_to_strengthen &&
            actionPlan.skills_to_strengthen.length
        ) {

            actionPlan.skills_to_strengthen.forEach(
                skill => {

                    const li =
                        document.createElement("li");

                    li.textContent = skill;

                    skillsList.appendChild(li);

                }
            );

        } else {

            const li =
                document.createElement("li");

            li.textContent =
                "No additional skills recommended.";

            skillsList.appendChild(li);
        }


        // ====================================================
        // APPLICATION PREPARATION
        // ====================================================

        const applicationList =
            document.getElementById(
                "applicationList"
            );


        clearElement(applicationList);


        if (
            actionPlan.application_preparation &&
            actionPlan.application_preparation.length
        ) {

            actionPlan.application_preparation.forEach(
                item => {

                    const li =
                        document.createElement("li");

                    li.textContent = item;

                    applicationList.appendChild(li);

                }
            );

        } else {

            const li =
                document.createElement("li");

            li.textContent =
                "No additional preparation recommendations.";

            applicationList.appendChild(li);
        }


        // ====================================================
        // CONDITIONAL REQUIREMENTS
        // ====================================================

        const conditionalList =
            document.getElementById(
                "conditionalList"
            );


        clearElement(conditionalList);


        const conditionalRequirements =
            eligibility.conditional_requirements || [];


        if (
            conditionalRequirements.length === 0
        ) {

            conditionalList.appendChild(
                createListItem(
                    "No conditional requirements identified.",
                    "requirement"
                )
            );

        } else {

            conditionalRequirements.forEach(
                requirement => {

                    conditionalList.appendChild(
                        createListItem(
                            requirement,
                            "requirement"
                        )
                    );

                }
            );
        }


        // ====================================================
        // READINESS CHECKLIST
        // ====================================================

        const readinessList =
            document.getElementById(
                "readinessList"
            );


        clearElement(readinessList);


        if (
            actionPlan.readiness_checklist &&
            actionPlan.readiness_checklist.length
        ) {

            actionPlan.readiness_checklist.forEach(
                item => {

                    const li =
                        document.createElement("li");

                    li.textContent = item;

                    readinessList.appendChild(li);

                }
            );

        } else {

            const li =
                document.createElement("li");

            li.textContent =
                "No readiness checklist available.";

            readinessList.appendChild(li);
        }


        // ====================================================
        // SOURCE
        // ====================================================

        const sourceUrl =
            document.getElementById(
                "sourceUrl"
            );


        sourceUrl.textContent =
            opportunity.url ||
            url;


        sourceUrl.href =
            opportunity.url ||
            url;


        document.getElementById(
            "evidence"
        ).textContent =
            opportunity.webpage_preview ||
            "Source webpage retrieved successfully.";


        // ====================================================
        // SHOW RESULTS
        // ====================================================

        results.classList.remove(
            "hidden"
        );


        // Scroll to results

        results.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


        console.log(
            "NAVIGATE analysis completed successfully."
        );

    }


    catch (error) {

        console.error(
            "NAVIGATE ERROR:",
            error
        );


        showError(
            "NAVIGATE encountered an error: " +
            error.message
        );

    }


    finally {

        loading.classList.add(
            "hidden"
        );


        analyzeButton.disabled = false;

        analyzeButton.textContent =
            "ANALYZE OPPORTUNITY";
    }

});
