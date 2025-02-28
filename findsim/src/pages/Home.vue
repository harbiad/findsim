<template>
  <div class="max-w-3xl py-12 mx-auto">
    <h2 class="font-bold text-lg text-gray-600 mb-4">
      Welcome {{ session.user }}!
    </h2>

    
  <div class="app">
  
    <SearchBar @update-records="searchDescription" />


    <div v-if="descriptions">
      Loading...
   </div>
    <div v-else>
      <ul>
        <li v-for="record in descriptions" :key="record">
           {{ record.description }}
        </li>
      </ul>
    </div>

  </div>


  <div class="flex flex-row space-x-2 mt-4">
      <!-- <Button @click="showDialog = true">Open Dialog</Button> -->
      <Button @click="session.logout.submit()">Logout</Button>
    </div>

    <!-- Dialog -->
    <Dialog title="Title" v-model="showDialog"> Dialog content </Dialog>
  </div>

</template>

<script setup>
import { ref } from 'vue'
import SearchBar from '../components/SearchBar.vue'
import { createResource, Dialog } from 'frappe-ui'
import { session } from '../data/session'
const records = ref([])

// Suppose we load this from a store or pass it from SearchBar via an event
function updateRecords(newRecords) {
  records.value = newRecords
}

const searchTerm = ref('')
  const descriptions = ref(null)
  // We can pass an event up or call a function that fetches from the server
  // function onSearch() {
  //   // Throttle or debounce in real implementation
  //   searchDescription(searchTerm.value)
  //   console.log('-->',searchTerm.value)
  // }
  
  const searchDescription = () => {
  // 1. Store the list resource in a variable
    descriptions.value = createListResource({
    doctype: 'Description',
    fields: ['name', 'description', 'old_number', 'sap_number'],
    auto: true,
    limit: 100,
  });

  // 5. Return or use the data
  console.log('descriptions-->', descriptions.value)
  return descriptions;
};
const ping = createResource({
  url: 'ping',
  auto: true,
})

const showDialog = ref(false)
</script>
