// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:srv/GetMove.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__SRV__DETAIL__GET_MOVE__STRUCT_H_
#define INTERFACES__SRV__DETAIL__GET_MOVE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'fen'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/GetMove in the package interfaces.
typedef struct interfaces__srv__GetMove_Request
{
  rosidl_runtime_c__String fen;
} interfaces__srv__GetMove_Request;

// Struct for a sequence of interfaces__srv__GetMove_Request.
typedef struct interfaces__srv__GetMove_Request__Sequence
{
  interfaces__srv__GetMove_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__srv__GetMove_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'move'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/GetMove in the package interfaces.
typedef struct interfaces__srv__GetMove_Response
{
  rosidl_runtime_c__String move;
} interfaces__srv__GetMove_Response;

// Struct for a sequence of interfaces__srv__GetMove_Response.
typedef struct interfaces__srv__GetMove_Response__Sequence
{
  interfaces__srv__GetMove_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__srv__GetMove_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__SRV__DETAIL__GET_MOVE__STRUCT_H_
