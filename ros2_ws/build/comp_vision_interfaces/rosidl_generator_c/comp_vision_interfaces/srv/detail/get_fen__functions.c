// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from comp_vision_interfaces:srv/GetFEN.idl
// generated code does not contain a copyright notice
#include "comp_vision_interfaces/srv/detail/get_fen__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
comp_vision_interfaces__srv__GetFEN_Request__init(comp_vision_interfaces__srv__GetFEN_Request * msg)
{
  if (!msg) {
    return false;
  }
  // structure_needs_at_least_one_member
  return true;
}

void
comp_vision_interfaces__srv__GetFEN_Request__fini(comp_vision_interfaces__srv__GetFEN_Request * msg)
{
  if (!msg) {
    return;
  }
  // structure_needs_at_least_one_member
}

bool
comp_vision_interfaces__srv__GetFEN_Request__are_equal(const comp_vision_interfaces__srv__GetFEN_Request * lhs, const comp_vision_interfaces__srv__GetFEN_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // structure_needs_at_least_one_member
  if (lhs->structure_needs_at_least_one_member != rhs->structure_needs_at_least_one_member) {
    return false;
  }
  return true;
}

bool
comp_vision_interfaces__srv__GetFEN_Request__copy(
  const comp_vision_interfaces__srv__GetFEN_Request * input,
  comp_vision_interfaces__srv__GetFEN_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // structure_needs_at_least_one_member
  output->structure_needs_at_least_one_member = input->structure_needs_at_least_one_member;
  return true;
}

comp_vision_interfaces__srv__GetFEN_Request *
comp_vision_interfaces__srv__GetFEN_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  comp_vision_interfaces__srv__GetFEN_Request * msg = (comp_vision_interfaces__srv__GetFEN_Request *)allocator.allocate(sizeof(comp_vision_interfaces__srv__GetFEN_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(comp_vision_interfaces__srv__GetFEN_Request));
  bool success = comp_vision_interfaces__srv__GetFEN_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
comp_vision_interfaces__srv__GetFEN_Request__destroy(comp_vision_interfaces__srv__GetFEN_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    comp_vision_interfaces__srv__GetFEN_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
comp_vision_interfaces__srv__GetFEN_Request__Sequence__init(comp_vision_interfaces__srv__GetFEN_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  comp_vision_interfaces__srv__GetFEN_Request * data = NULL;

  if (size) {
    data = (comp_vision_interfaces__srv__GetFEN_Request *)allocator.zero_allocate(size, sizeof(comp_vision_interfaces__srv__GetFEN_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = comp_vision_interfaces__srv__GetFEN_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        comp_vision_interfaces__srv__GetFEN_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
comp_vision_interfaces__srv__GetFEN_Request__Sequence__fini(comp_vision_interfaces__srv__GetFEN_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      comp_vision_interfaces__srv__GetFEN_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

comp_vision_interfaces__srv__GetFEN_Request__Sequence *
comp_vision_interfaces__srv__GetFEN_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  comp_vision_interfaces__srv__GetFEN_Request__Sequence * array = (comp_vision_interfaces__srv__GetFEN_Request__Sequence *)allocator.allocate(sizeof(comp_vision_interfaces__srv__GetFEN_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = comp_vision_interfaces__srv__GetFEN_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
comp_vision_interfaces__srv__GetFEN_Request__Sequence__destroy(comp_vision_interfaces__srv__GetFEN_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    comp_vision_interfaces__srv__GetFEN_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
comp_vision_interfaces__srv__GetFEN_Request__Sequence__are_equal(const comp_vision_interfaces__srv__GetFEN_Request__Sequence * lhs, const comp_vision_interfaces__srv__GetFEN_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!comp_vision_interfaces__srv__GetFEN_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
comp_vision_interfaces__srv__GetFEN_Request__Sequence__copy(
  const comp_vision_interfaces__srv__GetFEN_Request__Sequence * input,
  comp_vision_interfaces__srv__GetFEN_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(comp_vision_interfaces__srv__GetFEN_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    comp_vision_interfaces__srv__GetFEN_Request * data =
      (comp_vision_interfaces__srv__GetFEN_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!comp_vision_interfaces__srv__GetFEN_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          comp_vision_interfaces__srv__GetFEN_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!comp_vision_interfaces__srv__GetFEN_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `fen`
#include "rosidl_runtime_c/string_functions.h"

bool
comp_vision_interfaces__srv__GetFEN_Response__init(comp_vision_interfaces__srv__GetFEN_Response * msg)
{
  if (!msg) {
    return false;
  }
  // fen
  if (!rosidl_runtime_c__String__init(&msg->fen)) {
    comp_vision_interfaces__srv__GetFEN_Response__fini(msg);
    return false;
  }
  return true;
}

void
comp_vision_interfaces__srv__GetFEN_Response__fini(comp_vision_interfaces__srv__GetFEN_Response * msg)
{
  if (!msg) {
    return;
  }
  // fen
  rosidl_runtime_c__String__fini(&msg->fen);
}

bool
comp_vision_interfaces__srv__GetFEN_Response__are_equal(const comp_vision_interfaces__srv__GetFEN_Response * lhs, const comp_vision_interfaces__srv__GetFEN_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // fen
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->fen), &(rhs->fen)))
  {
    return false;
  }
  return true;
}

bool
comp_vision_interfaces__srv__GetFEN_Response__copy(
  const comp_vision_interfaces__srv__GetFEN_Response * input,
  comp_vision_interfaces__srv__GetFEN_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // fen
  if (!rosidl_runtime_c__String__copy(
      &(input->fen), &(output->fen)))
  {
    return false;
  }
  return true;
}

comp_vision_interfaces__srv__GetFEN_Response *
comp_vision_interfaces__srv__GetFEN_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  comp_vision_interfaces__srv__GetFEN_Response * msg = (comp_vision_interfaces__srv__GetFEN_Response *)allocator.allocate(sizeof(comp_vision_interfaces__srv__GetFEN_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(comp_vision_interfaces__srv__GetFEN_Response));
  bool success = comp_vision_interfaces__srv__GetFEN_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
comp_vision_interfaces__srv__GetFEN_Response__destroy(comp_vision_interfaces__srv__GetFEN_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    comp_vision_interfaces__srv__GetFEN_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
comp_vision_interfaces__srv__GetFEN_Response__Sequence__init(comp_vision_interfaces__srv__GetFEN_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  comp_vision_interfaces__srv__GetFEN_Response * data = NULL;

  if (size) {
    data = (comp_vision_interfaces__srv__GetFEN_Response *)allocator.zero_allocate(size, sizeof(comp_vision_interfaces__srv__GetFEN_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = comp_vision_interfaces__srv__GetFEN_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        comp_vision_interfaces__srv__GetFEN_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
comp_vision_interfaces__srv__GetFEN_Response__Sequence__fini(comp_vision_interfaces__srv__GetFEN_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      comp_vision_interfaces__srv__GetFEN_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

comp_vision_interfaces__srv__GetFEN_Response__Sequence *
comp_vision_interfaces__srv__GetFEN_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  comp_vision_interfaces__srv__GetFEN_Response__Sequence * array = (comp_vision_interfaces__srv__GetFEN_Response__Sequence *)allocator.allocate(sizeof(comp_vision_interfaces__srv__GetFEN_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = comp_vision_interfaces__srv__GetFEN_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
comp_vision_interfaces__srv__GetFEN_Response__Sequence__destroy(comp_vision_interfaces__srv__GetFEN_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    comp_vision_interfaces__srv__GetFEN_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
comp_vision_interfaces__srv__GetFEN_Response__Sequence__are_equal(const comp_vision_interfaces__srv__GetFEN_Response__Sequence * lhs, const comp_vision_interfaces__srv__GetFEN_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!comp_vision_interfaces__srv__GetFEN_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
comp_vision_interfaces__srv__GetFEN_Response__Sequence__copy(
  const comp_vision_interfaces__srv__GetFEN_Response__Sequence * input,
  comp_vision_interfaces__srv__GetFEN_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(comp_vision_interfaces__srv__GetFEN_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    comp_vision_interfaces__srv__GetFEN_Response * data =
      (comp_vision_interfaces__srv__GetFEN_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!comp_vision_interfaces__srv__GetFEN_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          comp_vision_interfaces__srv__GetFEN_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!comp_vision_interfaces__srv__GetFEN_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
