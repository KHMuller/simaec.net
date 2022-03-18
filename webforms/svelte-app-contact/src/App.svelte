<script>
    import { firestore } from "./firebase.js"

    // Form Switches, Validations and Response Variables
    let showForm = true;
    let showError = false;
    let isValidated = true;
    let isValidatedHidden = true;
    let messageRef = ''; 
                        
    // Form Fields Variables
    let firstname = '';
    let lastname = '';
    let email = '';
    let message = '';
    let topic = '';

    // Validation Flag of Required Variables
    $: isFirstname = (!isValidated && (!firstname || firstname === '')) ? false : true;
    $: isLastname = (!isValidated && (!lastname || lastname === '')) ? false : true;
    $: isEmail = (!isValidated && (!email || email === '')) ? false : true;
    $: isMessage = (!isValidated && (!message || message === '')) ? false : true;
    $: isTopic = (!isValidated && (!topic || topic === '')) ? false : true;
     
    // Form Hidden Variables
    let uuid = ('; '+document.cookie).split(`; uuid=`).pop().split(';')[0];
    let domain = window.location.hostname.replace('www.','');
    let valid_domains = ['muuuh.com','simaec.net','discoverymexico.com.mx']
    let url = window.location.href;

    // Check Hidden Variables 
    if (!uuid && uuid === '') {isValidatedHidden = false;}
    if (!valid_domains.includes(domain)) {isValidatedHidden = false;}        
    if (!url && url === '') {isValidatedHidden = false;}

    // isValidatedHidden = true; // Uncomment this line to test submission on localhost

    const handleSubmit = () => {
        isValidated = true;

        // Check Required Variables
        if (!firstname || firstname === '') {isValidated = false;}
        if (!lastname || lastname === '') {isValidated = false;}
        if (!email || email === '') {isValidated = false;}
        if (!message || message === '') {isValidated = false;}
        if (!topic && topic === '') {isValidated = false;}

        if (isValidated && isValidatedHidden) {
            const data = {
                dt_created: Math.round(new Date().getTime()/1000),
                firstname,
                lastname,
                email,
                topic,
                message,
		uuid,
                domain,
                url,
                source: 'contactform',
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
        <form name="contact" on:submit|preventDefault={handleSubmit}>
            <div>
                <label for="contact-firstname">First Name <span class="required">*</span></label>
                <input 
                    type="text" 
                    bind:value={firstname}
                    class:alert={!isFirstname} />
            </div>
            <div>
                <label for="contact-lastname">Last Name <span class="required">*</span></label>
                <input 
                    type="text"
                    bind:value={lastname}
                    class:alert={!isLastname} />
            </div>
            <div>
                <label for="contact-email">Email Address <span class="required">*</span></label>
                <input 
                    type="email" 
                    bind:value={email}
                    class:alert={!isEmail} />
            </div>
            <div>
                <label for="contact-topic">Topic <span class="required">*</span></label>
                <select 
                    bind:value={topic} 
                    class:alert={!isTopic} >
                    <option value="">Please Select</option>
                    <option value="I like Muuuh">I like Muuuh</option>
                    <option value="I have an idea how to improve Muuuh">I have an idea how to improve Muuuh</option>
                    <option value="I don't like Muuuh">I don't like Muuuh</option>
                    <option value="I have something else">I have something else</option>
                </select>
                {#if topic == 'I don\'t like Muuuh'}
                    <p class="note-box">There is a high chance that your message may be ignored ;)<br />Perhaps, you have a suggestion what can be improved?</p>
                {/if}
            </div>
            <div>
                <label for="contact-content">Message <span class="required">*</span></label>
                <textarea bind:value={message}  class:alert={!isMessage}></textarea>
            </div>
            <p>Your message will be stored and I will respond in timely fashion. Please make sure you enter the <strong>correct email address</strong>.</p>
            <div><button>Submit Message</button></div>  
        </form>
    {:else}
        <p class="note-box">Your data is only used to respond to your message and it will be deleted in less than 30 days after submission.</p>
        <p class="success-box">Your message has been received. <br />Reference: {messageRef}</p>
    {/if}

    {#if (!isValidated)}
        <p class="alert-box"><strong>All fields are mandatory</strong></p>
    {/if} 
    {#if showError}
        <p class="alert-box">An error has occurred and your message hasn't been saved.</p>
    {/if}
{:else}
    <p class="alert-box">Form has been disabled.</p>        
{/if}
