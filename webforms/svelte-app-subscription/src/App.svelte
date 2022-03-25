<script>
    import { firestore } from "./firebase.js"

    // Form Switches, Validations and Response Variables
    let showForm = true;
    let showError = false;
    let isValidated = true;
    let isValidatedHidden = true;
    let messageRef = '';

    // Form Fields Variables
    let email = '';
    let iagree = '';

    // Validation Flags of Required Fields
    $: isEmail = (!isValidated && (!email || email === '')) ? false : true;
    $: isIagree = (!isValidated && (!iagree || iagree === '')) ? false : true;    
    
    // Form Hidden Variables
    let uuid = ('; '+document.cookie).split(`; uuid=`).pop().split(';')[0];
    let domain = window.location.hostname.replace('www.','');
    let valid_domains = ['muuuh.com','simaec.net','discoverymexico.com.mx']
    let url = window.location.href;

    // Check Hidden Variables
    // Comment this out to test on localhost
    if (!uuid && uuid === '') {isValidatedHidden = false;}
    if (!valid_domains.includes(domain)) {isValidatedHidden = false;}        
    if (!url && url === '') {isValidatedHidden = false;}

    const handleSubmit = () => {
        isValidated = true;

        // Check Required Variables
        if (!email || email === '') {isValidated = false;}
        if (!iagree || iagree === '') {isValidated = false;}
        if (isValidated && isValidatedHidden) {
            const data = {
				dt_created: Math.round(new Date().getTime()/1000),
                email,
                iagree,
                domain,
                url,
                uuid,
                source: 'subscriptionform',
                secret: 'a-secret'
            }
			firestore.collection("webforms").add(data)
			.then((docRef) => {
				showForm = false;
				messageRef = docRef.id;
			})
			.catch((error) => {
				showError = true;
			});
        }
    };
</script>

{#if isValidatedHidden}
    {#if showForm}
        <form name="subscription" on:submit|preventDefault={handleSubmit}>
            <div class="form-headers">
                <p>Newsletter Subscription Form</p>
                <p>Simaec.net sends a bulletin about changes and additions to website and services. This form allows you to add your email address to the list of subscribers. You can unsubscribe anytime.</p>
            </div>            
            <div class="form-fields">
                <div>
                    <p>Please make sure you enter the <strong>correct email address</strong>.</p>
                    <label for="subscription-email">Email Address <span class="required">*</span></label>
                    <input
                        id="subscription-email"  
                        type="email" 
                        bind:value={email}
                        class:alert={!isEmail} />
                </div>
                <div>
                    <p><strong>Terms & Privacy Policy</strong> By using this form you express consent in receiving the newsletter. You further confirm that the submitted email address is yours and valid. Your email address will be stored savely and used only to send you the newsletter. A year after subscription, your email address will be removed automatically from the distribution list.</p>
                    <input 
                        id="subscription-iagree" 
                        type=checkbox 
                        bind:checked={iagree} 
                        class:alert={!isIagree} />
                    <label for="subscription-iagree">I accept to terms and privacy policy<span class="required">*</span></label>
                </div>
            </div>
            <div class="form-controls">
                <button>Subscribe</button>
            </div>
        </form>
    {:else}
        <p class="success-box">Your message has been received. <br />Reference: {messageRef}</p>
    {/if}

    {#if (!isValidated)}
        <p class="alert-box"><strong>All fields are mandatory</strong></p>
    {/if} 
    {#if showError}
        <p class="alert-box">An error has occurred. Your data hasn't been saved.</p>
    {/if}
{:else}
    <p class="note-box">Form is disabled.</p>        
{/if}
