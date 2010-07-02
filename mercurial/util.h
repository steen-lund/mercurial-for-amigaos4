/*
 util.h - utility functions for interfacing with the various python APIs.

 This software may be used and distributed according to the terms of
 the GNU General Public License, incorporated herein by reference.
*/

#ifndef _HG_UTIL_H_
#define _HG_UTIL_H_

#if PY_MAJOR_VERSION >= 3

#define IS_PY3K
#define PyInt_FromLong PyLong_FromLong
#define PyInt_AsLong PyLong_AsLong

#endif /* PY_MAJOR_VERSION */

/* Backports from 2.6 */
#if PY_VERSION_HEX < 0x02060000

#define Py_TYPE(ob) (ob)->ob_type
#define Py_SIZE(ob) (ob)->ob_size
#define PyVarObject_HEAD_INIT(type, size) PyObject_HEAD_INIT(type) size,

/* Shamelessly stolen from bytesobject.h */
#define PyBytesObject PyStringObject
#define PyBytes_Type PyString_Type

#define PyBytes_Check PyString_Check
#define PyBytes_CheckExact PyString_CheckExact
#define PyBytes_CHECK_INTERNED PyString_CHECK_INTERNED
#define PyBytes_AS_STRING PyString_AS_STRING
#define PyBytes_GET_SIZE PyString_GET_SIZE
#define Py_TPFLAGS_BYTES_SUBCLASS Py_TPFLAGS_STRING_SUBCLASS

#define PyBytes_FromStringAndSize PyString_FromStringAndSize
#define PyBytes_FromString PyString_FromString
#define PyBytes_FromFormatV PyString_FromFormatV
#define PyBytes_FromFormat PyString_FromFormat
#define PyBytes_Size PyString_Size
#define PyBytes_AsString PyString_AsString
#define PyBytes_Repr PyString_Repr
#define PyBytes_Concat PyString_Concat
#define PyBytes_ConcatAndDel PyString_ConcatAndDel
#define _PyBytes_Resize _PyString_Resize
#define _PyBytes_Eq _PyString_Eq
#define PyBytes_Format PyString_Format
#define _PyBytes_FormatLong _PyString_FormatLong
#define PyBytes_DecodeEscape PyString_DecodeEscape
#define _PyBytes_Join _PyString_Join
#define PyBytes_Decode PyString_Decode
#define PyBytes_Encode PyString_Encode
#define PyBytes_AsEncodedObject PyString_AsEncodedObject
#define PyBytes_AsEncodedString PyString_AsEncodedString
#define PyBytes_AsDecodedObject PyString_AsDecodedObject
#define PyBytes_AsDecodedString PyString_AsDecodedString
#define PyBytes_AsStringAndSize PyString_AsStringAndSize
#define _PyBytes_InsertThousandsGrouping _PyString_InsertThousandsGrouping

#endif /* PY_VERSION_HEX */

#endif /* _HG_UTIL_H_ */

