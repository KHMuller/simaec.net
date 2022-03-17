<script>
	import { firestore } from "./firebase.js"

	let showForm = true;
	let showError = false;
	let isValidForm = true;

	let firstname = '';
	let lastname = '';
	let email = '';
	let message = '';
	let topic = '';

	let messageRef = '';
	let uuid = ('; '+document.cookie).split(`; uuid=`).pop().split(';')[0];

	$: isFirstname = (!isValidForm && (!firstname || firstname === '')) ? false : true;
	$: isLastname = (!isValidForm && (!lastname || lastname === '')) ? false : true;
	$: isEmail = (!isValidForm && (!email || email === '')) ? false : true;
	$: isMessage = (!isValidForm && (!message || message === '')) ? false : true;
	$: isTopic = (!isValidForm && (!topic || topic === '')) ? false : true;        

	const handleSubmit = () => {
        isValidForm = true
        if (!firstname || firstname === '') {isValidForm = false;}
        if (!lastname || lastname === '') {isValidForm = false;}
        if (!email || email === '') {isValidForm = false;}
        if (!message || message === '') {isValidForm = false;}
        if (!topic && topic === '') {isValidForm = false;}
        if (!uuid && uuid === '') {isValidForm = false;} // document out to test locally
        if (isValidForm) {
            const data = {
				dt_created: Math.round(new Date().getTime()/1000),
                firstname,
                lastname,
                email,
                message,
                topic,
                uuid,
                source: 'contactform',
                secret: 'a-public-secret'
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

{#if showForm}
{#if (!uuid || uuid === '')}
	<p class="alert-box">This form requires that your browser accepts cookies.</p>
{/if}
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
    <div>
        {#if (!isValidForm)}
            <p class="alert-box"><strong>All fields are mandatory</strong></p>
        {/if}
        <button>Submit Message</button>
    </div>  
</form>
{:else}
	<p class="note-box">Your data is only used to respond to your message and it will be deleted in less than 30 days after submission.</p>
    <p class="success-box">Your message has been received. <br />Reference: {messageRef}</p>
{/if}

{#if showError}
	<p class="alert-box">An error has occurred and your message hasn't been saved.</p>
{/if}
