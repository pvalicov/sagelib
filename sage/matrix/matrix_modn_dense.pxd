cimport matrix_dense

cdef extern from "../ext/multi_modular.h":
    ctypedef unsigned long mod_int
    mod_int MOD_INT_OVERFLOW

cdef class Matrix_modn_dense(matrix_dense.Matrix_dense):
    cdef mod_int **_matrix
    cdef mod_int *_entries
    cdef mod_int p
    cdef mod_int gather
    cdef xgcd_eliminate (self, mod_int * row1, mod_int* row2, Py_ssize_t start_col)
    #cdef set_matrix(Matrix_modn_dense self, mod_int **m)
    #cdef mod_int **get_matrix(Matrix_modn_dense self)
    #cdef mod_int entry(self, mod_int i, mod_int j)
    cdef set_unsafe_int(self, Py_ssize_t i, Py_ssize_t j, int value)
    cdef _rescale_row_c(self, Py_ssize_t row, mod_int multiple, Py_ssize_t start_col)
    cdef _rescale_col_c(self, Py_ssize_t col, mod_int multiple, Py_ssize_t start_row)    
    cdef _add_multiple_of_row_c(self,  Py_ssize_t row_to, Py_ssize_t row_from,
                                mod_int multiple, Py_ssize_t start_col)
    cdef _add_multiple_of_column_c(self, Py_ssize_t col_to, Py_ssize_t col_from,
                                   mod_int multiple, Py_ssize_t start_row)
    
    cdef _init_linbox(self)
    cpdef _export_as_string(self)
        

cpdef is_Matrix_modn_dense(self)
