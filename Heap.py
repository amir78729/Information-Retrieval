# # Python3 implementation of Max heap
# import sys
#
#
# class MaxHeap:
#     def __init__(self, maxsize):
#         self.maxsize = maxsize
#         self.size = 0
#         self.heap = [(0, 0)] * (self.maxsize + 1)
#         self.heap[0] = (-1, sys.maxsize)
#         self.front = 1
#
#     # Function to return the position of parent for the node currently at pos
#     def parent(self, pos):
#         return pos // 2
#
#     # Function to return the position of the left child for the node currently  at pos
#     def leftChild(self, pos):
#         return 2 * pos
#
#     # Function to return the position of the right child for the node currently at pos
#     def rightChild(self, pos):
#
#         return (2 * pos) + 1
#
#     # Function that returns true if the passed node is a leaf node
#     def is_leaf(self, pos):
#         return (self.size // 2) <= pos <= self.size
#
#     # Function to swap two nodes of the heap
#     def swap(self, fpos, spos):
#         self.heap[fpos], self.heap[spos] = (self.heap[spos],self.heap[fpos])
#
#     # Function to heapify the node at pos
#     def max_heapify(self, pos):
#         # If the node is a non-leaf node and smaller
#         # than any of its child
#         if not self.is_leaf(pos):
#             if (self.heap[pos] < self.heap[self.leftChild(pos)] or
#                     self.heap[pos] < self.heap[self.rightChild(pos)]):
#
#                 # Swap with the left child and heapify
#                 # the left child
#                 if (self.heap[self.leftChild(pos)] >
#                         self.heap[self.rightChild(pos)]):
#                     self.swap(pos, self.leftChild(pos))
#                     self.max_heapify(self.leftChild(pos))
#
#                 # Swap with the right child and heapify
#                 # the right child
#                 else:
#                     self.swap(pos, self.rightChild(pos))
#                     self.max_heapify(self.rightChild(pos))
#
#     # Function to insert a node into the heap
#     def insert(self, element):
#         if self.size >= self.maxsize:
#             return
#         self.size += 1
#         self.heap[self.size] = element
#
#         current = self.size
#
#         # print(self.heap[current])
#         # print(self.heap[self.parent(current)])
#         while self.heap[current] > self.heap[self.parent(current)]:
#
#             self.swap(current, self.parent(current))
#             current = self.parent(current)
#
#
#     # Function to print the contents of the heap
#     def print_heap(self):
#         try:
#             self.heap.remove((-1, sys.maxsize))
#         except ValueError:
#             pass
#         for i in range(1, (self.size // 2) + 1):
#             print(" PARENT : " + str(self.heap[i]) +
#                   "\n\t LEFT CHILD : " + str(self.heap[2 * i]) +
#                   "\n\t RIGHT CHILD : " + str(self.heap[2 * i + 1]))
#
#     # Function to remove and return the maximum element from the heap
#     def extract_max(self):
#         popped = self.heap[self.front]
#         self.heap[self.front] = self.heap[self.size]
#         self.size -= 1
#         self.max_heapify(self.front)
#         return popped
#
#
# # Driver Code
# if __name__ == "__main__":
#     # print('The maxheap is ')
#
#     docs = [(1, 0.006021642733869699),
#             (2, 0.06558860040775293),
#             (3, 0.007078741382307875),
#             (4, 0.0030893547785879774),
#             (5, 0.022719770419340736),
#             (6, 0.007856149365815733),
#             (7, 0.006187145066735776),
#             (8, 0.00640989124608351),
#             (9, 0.1936971501764423),
#             (10, 0.008961092746030701)]
#
#
#     maxheap = MaxHeap(len(docs)+2)
#     for d in docs:
#         maxheap.insert(d)
#     maxheap.print_heap()
#     for i in range(7):
#
#         print(maxheap.extract_max())
#         # print()
#
#

# Python program for implementation of heap Sort

# To heapify subtree rooted at index i.
# n is size of heap


def heapify(arr, n, i):
    largest = i  # Initialize largest as root
    l = 2 * i + 1  # left = 2*i + 1
    r = 2 * i + 2  # right = 2*i + 2

    # See if left child of root exists and is
    # greater than root
    if l < n and arr[i][1] < arr[l][1]:
        largest = l

    # See if right child of root exists and is
    # greater than root
    if r < n and arr[largest][1] < arr[r][1]:
        largest = r

    # Change root, if needed
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # swap

        # Heapify the root.
        heapify(arr, n, largest)


# The main function to sort an array of given size
def heapSort(arr):
    n = len(arr)

    # Build a maxheap.
    # Since last parent will be at ((n//2)-1) we can start at that location.
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # swap
        heapify(arr, i, 0)
    res = arr[::-1]
    return res[:4]


# Driver code to test above
arr = [(3, 0.026366538469134372), (4, 0.03502408665140206), (5, 0.038308875408798584), (6, 0.011197565580587961), (7, 0.014278479396708945), (8, 0.08238434069802868), (9, 0.10622119680238401)]

arr = heapSort(arr)
n = len(arr)
print("Sorted array is")
for i in range(n):
    print(arr[i])