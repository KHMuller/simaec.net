<script>
    import Feedback from "./FeedbackForm.svelte";
    let modal;
</script>

<p class="modalShow"><button on:click={() => modal.show()}>Feedback</button></p>
<Feedback bind:this={modal} />
