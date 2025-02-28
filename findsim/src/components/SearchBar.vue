<template>
    <div class="search-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Search descriptions..."
        @input="searchDescription"
      />
    </div>
   

    
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  import { Card, ErrorMessage, createDocumentResource, createListResource } from 'frappe-ui';
  
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
    // filters: [
    //   ['description'],   //['description', 'like', `%${searchTerm.value}%`],
    // ],
    // 3. Use snake_case for fieldnames (standard practice)
    fields: ['name', 'description', 'old_number', 'sap_number'],
    // 4. Added auto: true for reactive updates
    auto: true,
    limit: 100,
  });

  // 5. Return or use the data
  console.log('descriptions-->', descriptions.value)
  return descriptions;
};
  // async function searchRecords(query) {
  //   try {
  //     // Using frappe.call for server-side function
  //     const response = await frappe.call({
  //       method: 'find_sim.api.search_description',
  //       args: { query },
  //     })
  //     // You’d typically emit an event with the results
  //     // e.g., `emit('update-records', response.message)`
  //   } catch (error) {
  //     console.error(error)
  //   }
  // }
  </script>
  