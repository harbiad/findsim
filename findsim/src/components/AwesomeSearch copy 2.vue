<template>
  <Button @click="post.reload()" :loading="post.loading">
    {{ post.fetched ? 'Reload' : 'Fetch data' }}
  </Button>
  <pre>{{ post.data }}</pre>
</template>

<script setup>

import { ref } from 'vue';
import { createResource } from 'frappe-ui';

let post = createResource({
    // partial rest api routes
    url: 'find_sim.api.search_description',
    
    method: 'GET',

    // // parameters
    params: {
      query: 'تين'
    },
    // // generate params from function
    // makeParams() {
    //   return {
    //     id: 1
    //   }
    // },

    // debounce request every 500ms
    debounce: 500,

    // initial data
    initialData: [],

    // make the first request automatically
    auto: true,

    // cache key to cache the resource
    // can be a string
    cache: 'post',
    // or an array that can be serialized
   // cache: ['post', '1'],
    // you can also pass reactive variable here
   // cache: ['post', postId]

    // events
    // before making the request
    beforeSubmit(params) {

    },
    // validate parameters before making request
    // validate(params) {
    //     if (!params.id) {
    //         // return a string message to throw an error
    //         return 'id is required'
    //     }
    // },
    // error can occur from failed request and validate function
    onError(error) {

    },
    // on successful response
    onSuccess(data) {
       
    },
    // transform data before setting it
    // transform(data) {
    //   for (let d of data) {
    //     d.open = false
    //   }
    //   return data
    // },
})
</script>