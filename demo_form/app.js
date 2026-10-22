/**
 * saarthi_member3_automation/demo_form/app.js
 * Client-side validation, review summary transition, and simulated confirmation handling.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Element references
    const form = document.getElementById("scheme-application-form");
    const formView = document.getElementById("form-entry-view");
    const reviewView = document.getElementById("review-summary-view");
    const errorSummaryBox = document.getElementById("error-summary-box");
    const errorList = document.getElementById("error-list");

    // Inputs
    const fullNameInput = document.getElementById("applicant-full-name");
    const dobInput = document.getElementById("applicant-dob");
    const genderSelect = document.getElementById("applicant-gender");
    const mobileInput = document.getElementById("applicant-mobile");
    const emailInput = document.getElementById("applicant-email");

    const houseInput = document.getElementById("address-house");
    const villageCityInput = document.getElementById("address-village-city");
    const districtInput = document.getElementById("address-district");
    const stateSelect = document.getElementById("address-state");
    const pinInput = document.getElementById("address-pin");

    const incomeInput = document.getElementById("scheme-income");
    const occupationSelect = document.getElementById("scheme-occupation");
    const consentCheckbox = document.getElementById("scheme-consent");
    const fileInput = document.getElementById("document-income-certificate");
    const fileNameDisplay = document.getElementById("file-name-display");

    // Action buttons
    const btnReview = document.getElementById("btn-review-application");
    const btnEdit = document.getElementById("btn-edit-application");
    const btnConfirm = document.getElementById("btn-confirm-application");

    // File selection display
    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            fileNameDisplay.textContent = `Selected Document: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        } else {
            fileNameDisplay.textContent = "";
        }
    });

    /**
     * Helper to show/hide field errors with human-friendly messages
     */
    function setFieldError(fieldId, errorMsg) {
        const errorElem = document.getElementById(`err-${fieldId}`);
        const inputElem = document.getElementById(fieldId) || document.querySelector(`[data-testid="${fieldId}"]`);
        
        if (errorMsg) {
            if (errorElem) {
                errorElem.textContent = errorMsg;
                errorElem.classList.add("visible");
            }
            if (inputElem && inputElem.classList) {
                inputElem.classList.add("input-error");
            }
        } else {
            if (errorElem) {
                errorElem.textContent = "";
                errorElem.classList.remove("visible");
            }
            if (inputElem && inputElem.classList) {
                inputElem.classList.remove("input-error");
            }
        }
    }

    /**
     * Clear all current errors
     */
    function clearAllErrors() {
        errorSummaryBox.style.display = "none";
        errorList.innerHTML = "";

        const fields = [
            "applicant-full-name", "applicant-dob", "applicant-gender",
            "applicant-mobile", "applicant-email", "address-house",
            "address-village-city", "address-district", "address-state",
            "address-pin", "scheme-income", "scheme-occupation",
            "scheme-category", "scheme-consent", "document-upload"
        ];
        fields.forEach(f => setFieldError(f, null));
    }

    /**
     * Validate form fields according to business rules
     */
    function validateForm() {
        clearAllErrors();
        const errors = [];

        // 1. Full name
        const fullName = fullNameInput.value.trim();
        if (!fullName) {
            const msg = "Please enter your full name.";
            errors.push(msg);
            setFieldError("applicant-full-name", msg);
        }

        // 2. Date of birth
        const dob = dobInput.value;
        if (!dob) {
            const msg = "Please enter your date of birth.";
            errors.push(msg);
            setFieldError("applicant-dob", msg);
        } else {
            const dobDate = new Date(dob);
            const today = new Date();
            if (dobDate > today) {
                const msg = "Date of birth cannot be in the future.";
                errors.push(msg);
                setFieldError("applicant-dob", msg);
            }
        }

        // 3. Gender
        if (!genderSelect.value) {
            const msg = "Please select your gender.";
            errors.push(msg);
            setFieldError("applicant-gender", msg);
        }

        // 4. Mobile number: 10 digits starting with 6, 7, 8, or 9
        const mobile = mobileInput.value.trim();
        const mobileRegex = /^[6-9]\d{9}$/;
        if (!mobile) {
            const msg = "Please enter your 10-digit mobile number.";
            errors.push(msg);
            setFieldError("applicant-mobile", msg);
        } else if (!mobileRegex.test(mobile)) {
            const msg = "The mobile number must be exactly 10 digits and start with 6, 7, 8, or 9.";
            errors.push(msg);
            setFieldError("applicant-mobile", msg);
        }

        // 5. Email (optional, but must be valid if given)
        const email = emailInput.value.trim();
        if (email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                const msg = "Please enter a valid email address.";
                errors.push(msg);
                setFieldError("applicant-email", msg);
            }
        }

        // 6. Address
        if (!houseInput.value.trim()) {
            const msg = "Please enter house or street address.";
            errors.push(msg);
            setFieldError("address-house", msg);
        }
        if (!villageCityInput.value.trim()) {
            const msg = "Please enter village or city.";
            errors.push(msg);
            setFieldError("address-village-city", msg);
        }
        if (!districtInput.value.trim()) {
            const msg = "Please enter district name.";
            errors.push(msg);
            setFieldError("address-district", msg);
        }
        if (!stateSelect.value) {
            const msg = "Please select your state or union territory.";
            errors.push(msg);
            setFieldError("address-state", msg);
        }

        // 7. PIN code: exactly 6 digits
        const pin = pinInput.value.trim();
        const pinRegex = /^\d{6}$/;
        if (!pin) {
            const msg = "Please enter your 6-digit PIN code.";
            errors.push(msg);
            setFieldError("address-pin", msg);
        } else if (!pinRegex.test(pin)) {
            const msg = "The PIN code must be exactly 6 digits.";
            errors.push(msg);
            setFieldError("address-pin", msg);
        }

        // 8. Income: non-negative number
        const income = incomeInput.value.trim();
        if (income === "") {
            const msg = "Please enter annual family income in rupees.";
            errors.push(msg);
            setFieldError("scheme-income", msg);
        } else if (Number(income) < 0 || isNaN(Number(income))) {
            const msg = "Annual income must be a non-negative number.";
            errors.push(msg);
            setFieldError("scheme-income", msg);
        }

        // 9. Occupation
        if (!occupationSelect.value) {
            const msg = "Please select your occupation.";
            errors.push(msg);
            setFieldError("scheme-occupation", msg);
        }

        // 10. Category (radio)
        const selectedCategory = document.querySelector('input[name="category"]:checked');
        if (!selectedCategory) {
            const msg = "Please select your social category.";
            errors.push(msg);
            setFieldError("scheme-category", msg);
        }

        // 11. Consent checkbox
        if (!consentCheckbox.checked) {
            const msg = "Please tick the consent checkbox to verify your details.";
            errors.push(msg);
            setFieldError("scheme-consent", msg);
        }

        // 12. Document upload
        if (!fileInput.files || fileInput.files.length === 0) {
            const msg = "Please upload an Income Certificate document.";
            errors.push(msg);
            setFieldError("document-upload", msg);
        } else {
            const file = fileInput.files[0];
            const allowedExts = [".pdf", ".jpg", ".jpeg", ".png"];
            const fileName = file.name.toLowerCase();
            const hasValidExt = allowedExts.some(ext => fileName.endsWith(ext));
            const maxSize = 2 * 1024 * 1024; // 2 MB

            if (!hasValidExt) {
                const msg = "The uploaded file must be in PDF, JPG, or PNG format.";
                errors.push(msg);
                setFieldError("document-upload", msg);
            } else if (file.size > maxSize) {
                const msg = "The document file size must not exceed 2 MB.";
                errors.push(msg);
                setFieldError("document-upload", msg);
            } else if (file.size === 0) {
                const msg = "The uploaded file is empty.";
                errors.push(msg);
                setFieldError("document-upload", msg);
            }
        }

        if (errors.length > 0) {
            errorSummaryBox.style.display = "block";
            errors.forEach(err => {
                const li = document.createElement("li");
                li.textContent = err;
                errorList.appendChild(li);
            });
            window.scrollTo({ top: 0, behavior: "smooth" });
            return false;
        }

        return true;
    }

    /**
     * Render the Review Summary view
     */
    function showReviewSummary() {
        const selectedCategory = document.querySelector('input[name="category"]:checked');
        const file = fileInput.files[0];

        document.getElementById("rev-applicant-full-name").textContent = fullNameInput.value.trim();
        document.getElementById("rev-applicant-dob").textContent = dobInput.value;
        document.getElementById("rev-applicant-gender").textContent = genderSelect.value;
        document.getElementById("rev-applicant-mobile").textContent = mobileInput.value.trim();
        document.getElementById("rev-applicant-email").textContent = emailInput.value.trim() || "Not provided";

        document.getElementById("rev-address-full").textContent = 
            `${houseInput.value.trim()}, ${villageCityInput.value.trim()}, Dist. ${districtInput.value.trim()}`;
        document.getElementById("rev-address-state-pin").textContent = 
            `${stateSelect.value} - ${pinInput.value.trim()}`;

        document.getElementById("rev-scheme-income").textContent = `₹ ${Number(incomeInput.value).toLocaleString('en-IN')}`;
        document.getElementById("rev-scheme-occupation").textContent = occupationSelect.value;
        document.getElementById("rev-scheme-category").textContent = selectedCategory ? selectedCategory.value : "";
        document.getElementById("rev-scheme-consent").textContent = consentCheckbox.checked ? "Confirmed by Applicant" : "No";
        document.getElementById("rev-document-name").textContent = file ? `${file.name} (${(file.size / 1024).toFixed(1)} KB)` : "None";

        formView.style.display = "none";
        reviewView.style.display = "block";
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    const btnCancel = document.getElementById("btn-cancel-application");

    // Event: Review Application Click
    btnReview.addEventListener("click", () => {
        if (validateForm()) {
            showReviewSummary();
        }
    });

    // Event: Edit Application Click
    btnEdit.addEventListener("click", () => {
        reviewView.style.display = "none";
        formView.style.display = "block";
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    // Event: Cancel Application Click
    if (btnCancel) {
        btnCancel.addEventListener("click", () => {
            if (confirm("Are you sure you want to cancel this application review? All progress will be reset.")) {
                sessionStorage.removeItem("saarthi_demo_submission");
                form.reset();
                fileNameDisplay.textContent = "";
                clearAllErrors();
                reviewView.style.display = "none";
                formView.style.display = "block";
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    }

    // Event: Confirm and Continue Click
    btnConfirm.addEventListener("click", () => {
        const selectedCategory = document.querySelector('input[name="category"]:checked');
        const file = fileInput.files[0];

        // Generate demo reference number (e.g. DEMO-8F29A4D1)
        const randomHex = Math.random().toString(36).substring(2, 10).toUpperCase();
        const demoRef = `DEMO-${randomHex}`;

        const submissionData = {
            reference: demoRef,
            applicant_name: fullNameInput.value.trim(),
            dob: dobInput.value,
            mobile: mobileInput.value.trim(),
            address: `${houseInput.value.trim()}, ${villageCityInput.value.trim()}, ${districtInput.value.trim()}`,
            state: stateSelect.value,
            pin: pinInput.value.trim(),
            income: incomeInput.value.trim(),
            category: selectedCategory ? selectedCategory.value : "",
            document: file ? file.name : "None",
            timestamp: new Date().toLocaleString()
        };

        // Store in sessionStorage and navigate
        sessionStorage.setItem("saarthi_demo_submission", JSON.stringify(submissionData));
        window.location.href = "receipt.html";
    });
});
