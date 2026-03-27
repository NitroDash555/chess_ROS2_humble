// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:srv/GetFEN.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__SRV__DETAIL__GET_FEN__BUILDER_HPP_
#define INTERFACES__SRV__DETAIL__GET_FEN__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/srv/detail/get_fen__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::srv::GetFEN_Request>()
{
  return ::interfaces::srv::GetFEN_Request(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace interfaces


namespace interfaces
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
  ::interfaces::srv::GetFEN_Response fen(::interfaces::srv::GetFEN_Response::_fen_type arg)
  {
    msg_.fen = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::srv::GetFEN_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::srv::GetFEN_Response>()
{
  return interfaces::srv::builder::Init_GetFEN_Response_fen();
}

}  // namespace interfaces

#endif  // INTERFACES__SRV__DETAIL__GET_FEN__BUILDER_HPP_
