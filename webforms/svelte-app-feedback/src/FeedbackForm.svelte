<script>
    import { firestore } from "./firebase.js"
    import { fade } from 'svelte/transition';
    
    let shown = false;

    export function show() { shown = true; }
    function hide() { shown = false; }

    let showForm = true;
    let showError = false;
    let showMissing = false;
    let isValidForm = true;   

    let meetmyneeds = '';
    let easytofind = '';
    let email = '';
    let comments = '';
    let url = window.location.href;
    let domain = window.location.hostname.replace('www.','');
    let valid_domains = ['simaec.net']

    let messageRef = '';
    let uuid = ('; '+document.cookie).split(`; uuid=`).pop().split(';')[0];

    $: isMeetmyneeds = (!isValidForm && (!meetmyneeds || meetmyneeds === '')) ? false : true;
    $: isEasytofind = (!isValidForm && (!easytofind || easytofind === '')) ? false : true;     

    const handleSubmit = () => {
        isValidForm = true;
        showMissing = false;
        if (!valid_domains.includes(domain)) {isValidForm = false;}
        if (!meetmyneeds && meetmyneeds === '') {isValidForm = false;}
        if (!easytofind && easytofind === '') {isValidForm = false;}
        if (!url && url === '') {isValidForm = false;}
        if (!uuid && uuid === '') {isValidForm = false;} // document out to test locally
        if (isValidForm) {
            const data = {
                dt_created: Math.round(new Date().getTime()/1000),
                meetmyneeds,
                easytofind,
                email,
                comments,
                url,
                uuid,
		source: 'feedbackform',
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
        } else {
            showMissing = true;
        }
    };
</script>
{#if shown}
    <section class="modalWrapper" transition:fade>
        <section class="modalContent">
            <p class="modalHide"><button on:click={() => hide()}>Close</button></p>
            <h3>Page Survey. We value your opinion!</h3>
            {#if showForm}
                {#if (!uuid || uuid === '')}
                    <p class="alertMessage">This form requires that your browser accepts cookies.</p>
                {/if}
                {#if showError}
                    <p class="alertMessage">An error has occurred. Your feedback hasn't been saved.</p>
                {/if}
                {#if showMissing}
                    <p class="alertMessage">Mandatory data missing. Please review the form.</p>
                {/if}                
                <form name="feedback" on:submit|preventDefault={handleSubmit}>
                    <input type="hidden" bind:value={uuid} />
                    <div class="formField" class:alert={!isMeetmyneeds}>
                        <h4>This Page meets my needs <span class="required">*</span></h4>
                        <table>
                            <thead>
                                <tr><th></th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th></th></tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Agree</td>
                                    <td><input type="radio" name="meetmyneeds" value="5" bind:group={meetmyneeds} /></td>
                                    <td><input type="radio" name="meetmyneeds" value="4" bind:group={meetmyneeds} /></td>
                                    <td><input type="radio" name="meetmyneeds" value="3" bind:group={meetmyneeds} /></td>
                                    <td><input type="radio" name="meetmyneeds" value="2" bind:group={meetmyneeds} /></td>
                                    <td><input type="radio" name="meetmyneeds" value="1" bind:group={meetmyneeds} /></td>
                                    <td>Disagree</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="formField" class:alert={!isEasytofind}>
                        <h4>This Page was easy to find <span class="required">*</span></h4>
                        <table>
                            <thead>
                                <tr><th></th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th></th></tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Agree</td>
                                    <td><input type="radio" name="easytofind" value="5" bind:group={easytofind} /></td>
                                    <td><input type="radio" name="easytofind" value="4" bind:group={easytofind} /></td>
                                    <td><input type="radio" name="easytofind" value="3" bind:group={easytofind} /></td>
                                    <td><input type="radio" name="easytofind" value="2" bind:group={easytofind} /></td>
                                    <td><input type="radio" name="easytofind" value="1" bind:group={easytofind} /></td>
                                    <td>Disagree</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="formField">
                        <h4>Do you like/dislike something in particular? How could this page serve you better?</h4>
                        <textarea bind:value={comments} placeholder="Your comments"></textarea>
                    </div>
                    <div class="formField">
                        <h4>Optional! Please provide your email address if you would like us to respond</h4>
                        <input type="email" bind:value={email} placeholder="Email address" />
                    </div>
                    <div class="formField">
                        <button>Submit Feedback</button>
                    </div>                  
                </form>
            {:else}
                <p class="successMessage">Thank you for taking the time in providing us your feedback.<br />Reference: {messageRef}</p>
            {/if}
        </section>
    </section>
{/if}
