// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from comp_vision_interfaces:srv/GetFEN.idl
// generated code does not contain a copyright notice

#ifndef COMP_VISION_INTERFACES__SRV__DETAIL__GET_FEN__BUILDER_HPP_
#define COMP_VISION_INTERFACES__SRV__DETAIL__GET_FEN__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "comp_vision_interfaces/srv/detail/get_fen__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace comp_vision_interfaces
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::comp_vision_interfaces::srv::GetFEN_Request>()
{
  return ::comp_vision_interfaces::srv::GetFEN_Request(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace comp_vision_interfaces


namespace comp_vision_interfaces
{

namespace srv
{

namespace builder
{

class Init_GetFEN_Response_fen
{
public:
  Init_GetFEN_Response_fen()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::comp_vision_interfaces::srv::GetFEN_Response fen(::comp_vision_interfaces::srv::GetFEN_Response::_fen_type arg)
  {
    msg_.fen = std::move(arg);
    return std::move(msg_);
  }

private:
  ::comp_vision_interfaces::srv::GetFEN_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::comp_vision_interfaces::srv::GetFEN_Response>()
{
  return comp_vision_interfaces::srv::builder::Init_GetFEN_Response_fen();
}

}  // namespace comp_vision_interfaces

#endif  // COMP_VISION_INTERFACES__SRV__DETAIL__GET_FEN__BUILDER_HPP_
