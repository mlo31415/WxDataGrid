from __future__ import annotations
from typing import Union, Optional
from dataclasses import dataclass
from abc import abstractmethod

import wx
import wx.grid

from HelpersPackage import IsInt
from WxHelpers import MessageBoxInput
from FanzineIssueSpecPackage import FanzineDateRange, FanzineDate

#================================================================
@dataclass
class ColDefinition:
    Name: str=""
    Width: int=100
    Type: str=""
    IsEditable: str="yes"
    preferred: str=""

    @property
    def Preferred(self) -> str:
        if self.preferred != "":
            return self.preferred
        return self.Name

    def Signature(self) -> int:     # ColDefinition
        return hash(self.Name)+hash(self.Width)+hash(self.Type)+hash(self.IsEditable)+hash(self.preferred)



@dataclass
class ColDefinitionsList:
    List: list[ColDefinition]

    # Implement 'in' as in "name" in ColDefinitionsList
    def __contains__(self, val: str) -> bool:       # ColDefinitionsList
        return any([x.Name == val or x.preferred == val for x in self.List])

    #--------------------------
    # Look up the index of a ColDefinition by name
    def __index__(self, val: str) -> int:       # ColDefinitionsList
        return self.index(val)

    def index(self, val: str) -> int:       # ColDefinitionsList
        if val not in self: # Calls __contains__
            raise IndexError
        return [x.Name == val or x.preferred == val for x in self.List].index(True)

    # --------------------------
    # Index can be a name or a list index
    def __getitem__(self, index: Union[str, int, slice]) -> Union[ColDefinition, ColDefinitionsList]:       # ColDefinitionsList
        if type(index) is str:     # The name of the column
            if index not in self: # Calls __contains__
                return ColDefinition(Name=index)
            return [x for x in self.List if x.Name == index or x.preferred == index][0]
        if type(index) is int:
            return self.List[index]
        if type(index) is slice:
            return ColDefinitionsList(self.List[index])
        raise KeyError

    #--------------------------
    def __delitem__(self, index: Union[str, int, slice]) -> None:       # ColDefinitionsList
        if type(index) is str:      # The name of the column
            if index in self: # Calls __contains__
                i=self.index(index)
                del self.List[i]
                return
            raise IndexError

        if type(index) is int:      # The index of the column
            del self.List[index]
            return

        if type(index) is slice:
            del self.List[index]
            return

        raise KeyError

    #--------------------------
    def __setitem__(self, index: Union[str, int, slice], value: ColDefinition) -> None:       # ColDefinitionsList
        if type(index) is str:      # The name of the column
            if index in self: # Calls __contains__
                i=self.index(index)
                self.List[i]=value
                return
            if value.Name == "":
                value.Name=index
            if value.Name != index:
                raise ValueError
            self.List.append(value)
            return

        if type(index) is int:      # The index of the column
            self.List[index]=value
            return

        if type(index) is slice:
            assert index[2] == 0
            self.List=self.List[index[0]:index[1]]+[value]+self.List[index[1]:]
            return

        raise KeyError

    def Signature(self) -> int:      # ColDefinitionsList
        return sum((i+1)*x.Signature() for i, x in enumerate(self.List))


    def __len__(self) -> int:       # ColDefinitionsList
        return len(self.List)

    def append(self, val: ColDefinition):       # ColDefinitionsList
        self.List.append(val)

    def __add__(self, val: ColDefinitionsList) ->ColDefinitionsList:       # ColDefinitionsList
        return ColDefinitionsList(self.List+val.List)

    def __iter__(self):       # ColDefinitionsList
        self._it=0
        return self

    def __next__(self):       # ColDefinitionsList
        if self._it == len(self.List):
            raise StopIteration
        val=self.List[self._it]
        self._it+=1
        return val


#================================================================
@dataclass(frozen=True)
class Color:
     # Define some RGB color constants
     LabelGray=wx.Colour(230, 230, 230)
     Pink=wx.Colour(255, 230, 230)
     LightGreen=wx.Colour(240, 255, 240)
     LightBlue=wx.Colour(240, 230, 255)
     Blue=wx.Colour(100, 100, 255)
     LightGray=wx.Colour(242, 242, 242)
     White=wx.Colour(255, 255, 255)
     Black=wx.Colour(0, 0, 0)


# A class to store and restore a selection
class Selection():
    def __init__(self, grid: wx.grid.Grid):
        self.selectedBlocks=grid.GetSelectedBlocks()
        self.selectedCols=grid.GetSelectedCols()
        self.selectedRows=grid.GetSelectedRows()
        self.selectedCells=grid.GetSelectedCells()


    def Restore(self, grid: wx.grid.Grid):      # Selection
        grid.ClearSelection()
        for row in self.selectedRows:
            grid.SelectRow(row, addToSelected=True)
        for col in self.selectedCols:
            grid.SelectCol(col, addToSelected=True)
        # The first two are mutually exclusive, so we can select without preserving previous selections.
        # But all these remaining selections have to be additive
        for block in self.selectedBlocks:
            grid.SelectBlock(block.TopLeft, block.BottomRight, True)
        # I don't know how to deal with this right now...
        if self.selectedCells:
            print("self.selectedCells exception")


    def Print(self, label: str):      # Selection
        for block in self.selectedBlocks:
            print(f"{label}: selected block({block.TopLeft}, {block.BottomRight})")
        selected=self.selectedCols
        print(f"{label}: selected cols: {selected}")
        selected=self.selectedRows
        print(f"{label}: selected rows: {selected}")
        for cell in self.selectedCells:
            print(f"{label}: selected cell({cell.x}, {cell.y})")


# An abstract class defining a row  of the GridDataSource
class GridDataRowClass:

    # Note that *all* signature calculation takes place in the external code on the Datasource and not on the wx grid.
    @abstractmethod
    def Signature(self) -> int:     # GridDataRowClass (abstract class)
        return 0

    # Get or set a value by name or column number in the grid
    @abstractmethod
    def __getitem__(self, index: Union[int, slice]) -> str:     # GridDataRowClass (abstract class)
        pass

    @abstractmethod
    def __setitem__(self, index: Union[str, int, slice], value: Union[str, int, bool]) -> None:     # GridDataRowClass (abstract class)
        pass

    @property
    def IsLinkRow(self) -> bool:     # GridDataRowClass (abstract class)
        return False            # Override only if needed

    @property
    def IsTextRow(self) -> bool:     # GridDataRowClass (abstract class)
        return False            # Override only if needed
    @IsTextRow.setter
    def IsTextRow(self, val: bool) -> None:
        assert False

    @property
    def CanDeleteColumns(self) -> bool:     # Override if column deletion is possible     # GridDataRowClass (abstract class)
        return True
    @abstractmethod
    def DelCol(self, icol) -> None:    # This *must* be implemented in the derived class because the data is so various
        pass

    # This needs to be implemented only if the datasource allows the addition of new columns
    @abstractmethod
    def append(self, val):     # GridDataRowClass (abstract class)
        pass

    @abstractmethod
    def IsEmptyRow(self) -> bool:     # GridDataRowClass (abstract class)
        assert False


# An abstract class which defines the structure of a data source for the Grid class
class GridDataSource():

    def __init__(self):     # GridDataSource() abstract class
        self._colDefs: ColDefinitionsList=ColDefinitionsList([])
        self._allowCellEdits: list[tuple[int, int]]=[]     # A list of cells where editing has been permitted by overriding a "maybe" for the col
        self._gridDataRowClass: GridDataRowClass=None
        # self.Rows must be supplied by the derived class


    @property
    def Element(self):     # GridDataSource() abstract class
        return self._gridDataRowClass

    @property
    def ColDefs(self) -> ColDefinitionsList:     # GridDataSource() abstract class
        return self._colDefs
    @ColDefs.setter
    def ColDefs(self, cds: ColDefinitionsList):     # GridDataSource() abstract class
        self._colDefs=cds

    @property
    def ColHeaders(self) -> list[str]:     # GridDataSource() abstract class
        return [l.Name for l in self.ColDefs]

    @property
    def AllowCellEdits(self) -> list[tuple[int, int]]:     # GridDataSource() abstract class
        return self._allowCellEdits
    @AllowCellEdits.setter
    def AllowCellEdits(self, val: list[tuple[int, int]]) -> None:     # GridDataSource() abstract class
        self._allowCellEdits=val

    @property
    def NumCols(self) -> int:     # GridDataSource() abstract class
        return len(self.ColDefs)

    @property
    @abstractmethod
    def NumRows(self) -> int:     # GridDataSource() abstract class
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> GridDataRowClass:     # GridDataSource() abstract class
        pass

    @abstractmethod
    def __setitem__(self, index: int, val: GridDataRowClass) -> None:     # GridDataSource() abstract class
        pass

    @property
    @abstractmethod
    def Rows(self) -> list[GridDataRowClass]:     # Types of list elements needs to be undefined since we don't know what they will be.     # GridDataSource() abstract class
        pass
    @Rows.setter
    @abstractmethod
    def Rows(self, rows: list[GridDataRowClass]) -> None:     # GridDataSource() abstract class
        pass

    def AppendEmptyRows(self, num: int = 1):     # GridDataSource() abstract class
        self.InsertEmptyRows(self.NumRows, num)

    def IsEmptyRow(self, i: int) -> bool:     # GridDataSource() abstract class
        return self.Rows[i].IsEmptyRow()

    @abstractmethod
    def InsertEmptyRows(self, insertat: int, num: int=1) -> None:     # GridDataSource() abstract class
        pass

    @property
    def CanAddColumns(self) -> bool:     # GridDataSource() abstract class
        return False            # Override this if adding columns is allowed

    @property
    def CanEditColumnHeaders(self) -> bool:     # GridDataSource() abstract class
        return False            # Override this if editing the column headers is allowed

    @property
    def CanMoveColumns(self) -> bool:     # GridDataSource() abstract class
        return True             # Override if columns can't be moved


    # Fnd the index of a possible header in the column header. -1 in not found
    def ColHeaderIndex(self, s: str, CaseSensitive=False) -> int:     # GridDataSource() abstract class
        if CaseSensitive:
            if s in self.ColHeaders:
                return self.ColHeaders.index(s)
        else:
            temp=[header.lower() for header in self.ColHeaders]
            if s.lower() in temp:
                return temp.index(s.lower())
        return -1

    # Insert a new column
    # And index of -1 appends
    def InsertColumnHeader(self, index: int, cdef: str | ColDefinition):     # GridDataSource() abstract class
        if type(cdef) is str:
            c=self._colDefs.index(cdef)
        c=ColDefinitionsList([cdef])
        if index >= 0:
            self._colDefs=self._colDefs[:index]+c+self._colDefs[index:]
        else:
            self._colDefs=self._colDefs+c


    # Take a box of row/col indexes such as used in a selection: (top, left, bottom, right)
    # and limit it to the rows and columns actually currently defined
    def LimitBoxToActuals(self, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:     # GridDataSource() abstract class
        top, left, bottom, right=box
        if top < 0:
            top=0
        if bottom > self.NumRows-1:
            bottom=self.NumRows-1
        if right < 0:
            right=0
        if left > self.NumCols-1:
            left=self.NumCols-1
        return top, left, bottom, right

    @property
    def SpecialTextColor(self) -> Optional[Color]:      #TODO: Is SpecialTextColor needed any more?     # GridDataSource() abstract class
        return None
    @SpecialTextColor.setter
    def SpecialTextColor(self, val: Optional[Color]) -> None:     # GridDataSource() abstract class
        return


################################################################################
class DataGrid():

    def __init__(self, grid: wx.grid.Grid):         # DataGrid
        self._grid: wx.grid.Grid=grid

        self._datasource: GridDataSource=GridDataSource()
        self.clipboard=None         # The grid's clipboard
        self.cntlDown: bool=False         # There's no cntl-key currently down
        self.clickedColumn: Optional[int]=None
        self.clickedRow: Optional[int]=None


    # --------------------------------------------------------
    def AllowCellEdit(self, irow: int, icol: int) -> None:        # DataGrid
        self._datasource.AllowCellEdits.append((irow, icol))
        if irow >= self.NumRows:
            self._grid.AppendRows(irow-self.NumRows+1)

    # Make text lines to be merged and editable
    def MakeTextLinesEditable(self) -> None:        # DataGrid
        for irow, row in enumerate(self._datasource.Rows):
            if row.IsTextRow or row.IsLinkRow:
                for icol, ch in enumerate(self._datasource.ColDefs):
                    if ch.IsEditable == "maybe":
                        self.AllowCellEdit(irow, icol)


    # --------------------------------------------------------
    # Get a cell value
    # Note that this does not change the underlying data
    @abstractmethod
    def __getitem__(self, index: int):        # DataGrid
        return self._grid[index]

    # --------------------------------------------------------
    @property
    def NumCols(self) -> int:        # DataGrid
        return self._grid.NumberCols
    @NumCols.setter
    # Note that this actually changes the number of columns in the grid by adding or deleting from the end
    # It does not change the ColDefs
    def NumCols(self, nCols: int) -> None:        # DataGrid
        if self._grid.NumberCols == nCols:
            return
        if self._grid.NumberCols > nCols:
            self._grid.DeleteCols(nCols, self._grid.NumberCols-nCols)
        else:
            self._grid.AppendCols(nCols-self._grid.NumberCols)

    # --------------------------------------------------------
    @property
    def NumRows(self) -> int:        # DataGrid
        return self._grid.NumberRows

    # --------------------------------------------------------
    @property
    def Datasource(self) -> GridDataSource:         # DataGrid
        return self._datasource
    @Datasource.setter
    def Datasource(self, val: GridDataSource):
        self._datasource=val

    # --------------------------------------------------------
    @property
    def Grid(self):        # DataGrid
        return self._grid

    # --------------------------------------------------------
    def AppendRows(self, nrows: int) -> None:        # DataGrid
        self.ExpandDataSourceToInclude(self.NumRows+nrows)

    # --------------------------------------------------------
    # Insert one or more empty rows in the data source.
    # Then refresh the grid
    def InsertEmptyRows(self, irow: int, nrows: int) -> None:        # DataGrid
        self.Datasource.InsertEmptyRows(irow, nrows)    # Insert the requisite number of rows at irow

        # Now update the editable status of non-editable columns
        # All row numbers >= irow are incremented by nrows
        for i, (row, col) in enumerate(self._datasource.AllowCellEdits):
            if row >= irow:
                self.Datasource.AllowCellEdits[i]=(row+nrows, col)

        self.RefreshWxGridFromDatasource()

    # --------------------------------------------------------
    def DeleteRows(self, irow: int, numrows: int=1):        # DataGrid
        if irow >= self.Datasource.NumRows:
            return

        numrows=min(numrows, self.Datasource.NumRows-irow)  # If the request goes beyond the end of the data, ignore the extras
        del self.Datasource.Rows[irow:irow+numrows]

        # We also need to drop entries in AllowCellEdits which refer to this row and adjust the indexes of ones referring to all later rows
        for index, (i, j) in enumerate(self.Datasource.AllowCellEdits):
            if i >= irow:
                if i < irow+numrows:
                    # Mark it for deletion
                    self.Datasource.AllowCellEdits[index]=(-1, -1)  # We tag them rather than deleting them so we don't mess up the enumerate loop
                else:
                    # Update it to the new row indexing scheme
                    self.Datasource.AllowCellEdits[index]=(i-numrows, j)
        self.Datasource.AllowCellEdits=[x for x in self.Datasource.AllowCellEdits if x[0] != -1]  # Get rid of the tagged entries


    # Scroll so as to make as many as possible of the rows visible
    def MakeRowsVisible(self, rows: list[int]) -> None:         # DataGrid
        # Find the bounding rows
        low=min(rows)
        high=max(rows)

        # If either is not visible, make it visible
        # Note that this can't deal with the too many rows for the window case
        if not self._grid.IsVisible(low, 1):
            self._grid.MakeCellVisible(low, 1)
        if not self._grid.IsVisible(high, 1):
            self._grid.MakeCellVisible(high, 1)


    # --------------------------------------------------------
    def AppendEmptyCols(self, ncols: int) -> None:        # DataGrid
        self._grid.AppendCols(ncols)


    # --------------------------------------------------------
    def SetColHeaders(self, coldefs: ColDefinitionsList) -> None:        # DataGrid
        # If necessary, change the grid to match the ColDefs
        self.NumCols=len(coldefs)

        # Add the column headers
        for i, cd in enumerate(coldefs):
            self._grid.SetColLabelValue(i, cd.Preferred)

    # --------------------------------------------------------
    def AutoSizeColumns(self):        # DataGrid
        self._grid.AutoSizeColumns()
        if len(self._datasource.ColDefs) == self._grid.NumberCols-1:
            iCol=0
            for cd in self._datasource.ColDefs:
                w=self._grid.GetColSize(iCol)
                if w < cd.Width:
                    self._grid.SetColSize(iCol, cd.Width)
                iCol+=1

    # --------------------------------------------------------
    def SetCellBackgroundColor(self, irow: int, icol: int, color):        # DataGrid
        self._grid.SetCellBackgroundColour(irow, icol, color)

    # --------------------------------------------------------
    # Row, col are Grid coordinates
    def ColorCellByValue(self, irow: int, icol: int) -> None:        # DataGrid
        # Start by setting color to white
        self.SetCellBackgroundColor(irow, icol, Color.White)

        # Deal with col overflow
        if icol >= len(self._datasource.ColDefs):
            return

        if irow >= self.Datasource.NumRows:
            # These are trailing rows and should get default formatting
            # Row overflow is permitted and extra rows (rows in the grid, but not in the datasource) are colored generically
            self._grid.SetCellSize(irow, icol, 1, 1)  # Eliminate any spans
            self._grid.SetCellFont(irow, icol, self._grid.GetCellFont(irow, icol).GetBaseFont())
            if self._datasource.ColDefs[icol].IsEditable == "no" or self._datasource.ColDefs[icol].IsEditable == "maybe":
                self.SetCellBackgroundColor(irow, icol, Color.LightGray)
            return

        # We're now in a row that includes data
        # First turn off any special formatting
        self._grid.SetCellFont(irow, icol, self._grid.GetCellFont(irow, icol).GetBaseFont())
        self.SetCellBackgroundColor(irow, icol, Color.White)
        self._grid.SetCellTextColour(irow, icol, Color.Black)

        # If the row is a text row and if there's a special text color
        # The special text color can be a color, which we then use to color the text or
        # It can be anything else, in which case we BOLD the text.
        if irow < self._datasource.NumRows and self._datasource.Rows[irow].IsTextRow and self._datasource.SpecialTextColor is not None:
            if self._datasource.SpecialTextColor is not None:
                if type(self._datasource.SpecialTextColor) is Color:
                    self.SetCellBackgroundColor(irow, icol, self._datasource.SpecialTextColor)
                else:
                    self._grid.SetCellFont(irow, icol, self._grid.GetCellFont(irow, icol).Bold())

        # If the row is a link row give it the look of a link
        elif irow < self._datasource.NumRows and self._datasource.Rows[irow].IsLinkRow:
            # Locate the "Display Name" column
            if not "Display Name" in self.Datasource.ColHeaders:
                assert False  # This should never happen
            colnum=self.Datasource.ColHeaders.index("Display Name")
            if icol < colnum:
                self._grid.SetCellFont(irow, icol, self._grid.GetCellFont(irow, icol).Underlined())

        # If the column is not editable, color it light gray regardless of its value
        elif self._datasource.ColDefs[icol].IsEditable == "no":
            self.SetCellBackgroundColor(irow, icol, Color.LightGray)
        elif self._datasource.ColDefs[icol].IsEditable == "maybe" and (irow, icol) not in self._datasource.AllowCellEdits:
            self.SetCellBackgroundColor(irow, icol, Color.LightGray)

        else:
            # If it *is* editable or potentially editable, then color it according to its value
            # We skip testing for "str"-type columns since anything at all is OK in a str column
            if not self._datasource.IsEmptyRow(irow):  # Don't bother filling in colors in completely empty rows
                val=self._grid.GetCellValue(irow, icol)
                if self._datasource.ColDefs[icol].Type == "int":
                    if val is not None and val != "" and not IsInt(val):
                        self.SetCellBackgroundColor(irow, icol, Color.Pink)
                elif self._datasource.ColDefs[icol].Type == "date range":
                    if val is not None and val != "" and FanzineDateRange().Match(val).IsEmpty():
                        self.SetCellBackgroundColor(irow, icol, Color.Pink)
                elif self._datasource.ColDefs[icol].Type == "date":
                    if val is not None and val != "" and FanzineDate().Match(val).IsEmpty():
                        self.SetCellBackgroundColor(irow, icol, Color.Pink)
                elif self._datasource.ColDefs[icol].Type == "required str":
                    if val is None or len(val) == 0:
                        self.SetCellBackgroundColor(irow, icol, Color.Pink)

        # Special handling for URLs: we add an underline and paint the text blue
        if self._datasource.ColDefs[icol].Type == "url":
            val=self._grid.GetCellValue(irow, icol)
            font=self._grid.GetCellFont(irow, icol)
            if val is not None and val != "" and self._datasource.Rows[irow].URL:
                self._grid.SetCellTextColour(irow, icol, Color.Blue)
                font.MakeUnderlined()
                self._grid.SetCellFont(irow, icol, font)
            else:
                # self._grid.SetCellTextColour(irow, icol, Color.Blue)
                font.SetUnderlined(False)
                self._grid.SetCellFont(irow, icol, font)

    # --------------------------------------------------------
    def ColorCellsByValue(self):        # DataGrid
        # Analyze the data and highlight cells where the data type doesn't match the header.  (E.g., Volume='August', Month='17', year='20')
        # Col 0 is a number and 3 is a date and the rest are strings.   We walk the rows checking the type of data in that column.
        for iRow in range(self._grid.NumberRows):
            for iCol in range(self._grid.NumberCols):
                self.ColorCellByValue(iRow, iCol)

    # --------------------------------------------------------
    def GetSelectedRowRange(self) -> Optional[tuple[int, int]]:        # DataGrid
        rows=self._grid.GetSelectedRows()
        sel=self._grid.GetSelectionBlockTopLeft()
        if len(sel) > 0:
            rows.append(sel[0][0])
        sel=self._grid.GetSelectionBlockBottomRight()
        if len(sel) > 0:
            rows.append(sel[0][0])
        for cell in self._grid.GetSelectedCells():
            rows.append(cell[0])

        if len(rows) > 0:
            return (min(rows), max(rows))

        return None

    # ------------------
    def RefreshWxGridFromDatasource(self, IgnoreCurrentGrid=False):        # DataGrid
        selection=Selection(self._grid)

        # Record the visible lines so we can make them visible again later
        visibleRows=[]
        if self._grid.NumberCols > 0:
            visibleRows=[i for i in range(self._grid.NumberRows) if self._grid.IsVisible(i, 0, wholeCellVisible=True)]

        scroll=self._grid.ScrollLineX

        self._grid.ClearGrid()
        if self._grid.NumberRows > 0:
            self._grid.DeleteRows(0, self._grid.NumberRows)

        self.SetColHeaders(self._datasource.ColDefs)

        # Put in the requisite rows plus 5 spares
        self._grid.AppendRows(self._datasource.NumRows+5)

        # Fill in the cells
        for irow in range(self._datasource.NumRows):
            if self._datasource.Rows[irow].IsTextRow:
                self._grid.SetCellSize(irow, 0, 1, self.NumCols)   # Make text rows all one cell

            elif self._datasource.Rows[irow].IsLinkRow:    # If a grid allows IsLinkRow to be set, its Datasource must have a column labelled "Display Name"
                # Locate the "Display Name" column
                if not "Display Name" in self._datasource.ColHeaders:
                    assert False  # This should never happen
                colnum=self._datasource.ColHeaders.index("Display Name")
                self._grid.SetCellSize(irow, 0, 1, colnum)  # Merge all the cells up to the display name column
                self._grid.SetCellSize(irow, colnum, 1, self.NumCols-colnum)  # Merge the rest the cells into a second column

            else:
                self._grid.SetCellSize(irow, 0, 1, 1)  # Set as normal unspanned cell

            for icol in range(len(self._datasource.ColDefs)):
                val=self._datasource[irow][icol]
                if val is None:
                    val=""
                else:
                    val=str(val)
                self._grid.SetCellValue(irow, icol, val)

        self.ColorCellsByValue()
        self.AutoSizeColumns()
        #self._grid.AutoSize()

        if not IgnoreCurrentGrid:
            selection.Restore(self._grid)
            # Make the lines which were visible before we messed with things visible again
            if visibleRows:
                self._grid.MakeCellVisible(min(visibleRows), 0)
                self._grid.MakeCellVisible(max(visibleRows), 0)


    #--------------------------------------------------------
    # Move a block of rows within the data source
    # All row numbers are logical
    # Oldrow is the 1st row of the block to be moved
    # Newrow is the target position to which oldrow is moved
    def MoveRows(self, oldrow: int, numrows: int, newrow: int):        # DataGrid
        rows=self._datasource.Rows

        dest=newrow
        start=oldrow
        end=oldrow+numrows-1
        if newrow < oldrow:
            # Move earlier
            b1=rows[0:dest]
            i1=list(range(0, dest))
            b2=rows[dest:start]
            i2=list(range(dest, start))
            b3=rows[start:end+1]
            i3=list(range(start, end+1))
            b4=rows[end+1:]
            i4=list(range(end+1, len(rows)))
        else:
            # Move later
            b1=rows[0:start]
            i1=list(range(0, start))
            b2=rows[start:end+1]
            i2=list(range(start, end+1))
            b3=rows[end+1:end+1+dest-start]
            i3=list(range(end+1, end+1+dest-start))
            b4=rows[end+1+dest-start:]
            i4=list(range(end+1+dest-start, len(rows)))

        rows=b1+b3+b2+b4
        self._datasource.Rows=rows

        tpermuter=i1+i3+i2+i4
        permuter=[-1]*len(tpermuter)     # This next bit of code inverts the permuter into its anti-permuter. (There ought to be a more elegant way to generate it!)
        for i, r in enumerate(tpermuter):
            permuter[r]=i

        # Log("\npermuter: "+str(permuter))
        # Log("old editable rows: "+str(sorted(list(set([x[0] for x in self._datasource.AllowCellEdits])))))
        # Now use the permuter to update the row numbers of the cells which are allowed to be edited
        for i, (row, col) in enumerate(self._datasource.AllowCellEdits):
            try:
                self._datasource.AllowCellEdits[i]=(permuter[row], col)
            except:
                pass
        # Log("new editable rows: "+str(sorted(list(set([x[0] for x in self._datasource.AllowCellEdits])))))


    #--------------------------------------------------------
    # Move a block of rows within the data source
    # All row numbers are logical
    # Oldrow is the 1st row of the block to be moved
    # Newrow is the target position to which oldrow is moved
    def MoveCols(self, oldcol: int, numcols: int, newcol: int):        # DataGrid
        rows=self._datasource.Rows

        dest=newcol
        start=oldcol
        end=oldcol+numcols-1
        print(f"MoveCols: {start=}  {end=}  {numcols=}  {dest=}")
        if newcol < oldcol:
            # Move earlier
            i1=list(range(0, dest))
            i2=list(range(dest, start))
            i3=list(range(start, end+1))
            i4=list(range(end+1, len(rows)))
            # print(f"{i1=}  {i2=}  {i3=}  {i4=}")
        else:
            # Move Later
            i1=list(range(0, start))
            i2=list(range(start, end+1))
            i3=list(range(end+1, end+1+dest-start))
            i4=list(range(end+1+dest-start, len(rows)))
            # print(f"{i1=}  {i2=}  {i3=}  {i4=}")

        tpermuter: list[int]=i1+i3+i2+i4
        permuter: list[int]=[-1]*len(tpermuter)     # This next bit of code inverts the permuter. (There ought to be a more elegant way to generate it!)
        for i, r in enumerate(tpermuter):
            permuter[r]=i

        for row in rows:
            temp=[-1]*self.NumCols
            for i in range(self.NumCols):
                temp[i]=row[i]
            for i in range(self.NumCols):
                row[permuter[i]]=temp[i]
        # Log("permuter: "+str(permuter))
        # Log("tpermuter: "+str(tpermuter))
        # Log("old editable rows: "+str(sorted(list(set([x[0] for x in self._datasource.AllowCellEdits])))))

        # Move the column labels
        temp: list=[None]*self.NumCols
        for i in range(self.NumCols):
            temp[i]=self.Datasource.ColDefs[i]
        for i in range(self.NumCols):
            self.Datasource.ColDefs[permuter[i]]=temp[i]

        # Now use the permuter to update the row numbers of the cells which are allowed to be edited
        for i, (row, col) in enumerate(self._datasource.AllowCellEdits):
            try:
                self._datasource.AllowCellEdits[i]=(permuter[row], col)
            except:
                pass
        # Log("new editable rows: "+str(sorted(list(set([x[0] for x in self._datasource.AllowCellEdits])))))


    # ------------------
    def CopyCells(self, top: int, left: int, bottom: int, right: int) -> None:        # DataGrid
        self.clipboard=[]
        for iRow in range(top, bottom+1):
            v=[]
            for jCol in range(left, right+1):
                v.append(self._datasource[iRow][jCol])
            self.clipboard.append(v)


    # ------------------
    def PasteCells(self, top: int, left: int) -> None:        # DataGrid
        # We paste the clipboard data into the block of the same size with the upper-left at the mouse's position
        # Might some of the new material be outside the current bounds?  If so, add some blank rows and/or columns

        # Define the bounds of the paste-to box
        pasteTop=top
        pasteBottom=top+len(self.clipboard)-1
        pasteLeft=left
        pasteRight=left+len(self.clipboard[0])-1

        # Does the paste-to box extend beyond the end of the available rows?  If so, extend the available rows.
        num=pasteBottom-len(self._datasource.Rows)+1
        if num > 0:
            self.Datasource.InsertEmptyRows(self.Datasource.NumRows, num)
        # Refresh the datagrid from the Datasource to make it also bigger
        self.RefreshWxGridFromDatasource()

        # Copy the cells from the clipboard to the grid in lstData.
        for i, row in enumerate(self.clipboard, start=pasteTop):
            for j, cellval in enumerate(row, start=pasteLeft):
                self._datasource[i][j]=cellval
        self.RefreshWxGridFromDatasource()

    # --------------------------------------------------------
    # Expand the grid's data source so that the local item (irow, icol) exists.
    def ExpandDataSourceToInclude(self, irow: int, icol: int=0) -> None:        # DataGrid
        assert irow >= 0 and icol >= 0

        # Add new rows if needed
        while irow >= self._datasource.NumRows:
            self._datasource.InsertEmptyRows(self._datasource.NumRows, irow-self._datasource.NumRows+1)

        # And add new columns
        # Many data sources do not allow expanding the number of columns, so check that first
        assert icol < len(self._datasource.ColDefs) or self._datasource.CanAddColumns
        if self._datasource.CanAddColumns:
            while icol >= len(self._datasource.ColDefs):
                self._datasource.ColDefs.append(ColDefinition())
                for j in range(self._datasource.NumRows):
                    self._datasource.Rows[j].append("") # Note that append is implemented only when columns can be added

    #------------------------------------
    # In many even handlers we need to save the click location
    def SaveClickLocation(self, event):        # DataGrid
        self.clickedColumn=event.GetCol()
        self.clickedRow=event.GetRow()

    #------------------
    def OnGridCellChanged(self, event):        # DataGrid
        #self.EvtHandlerEnabled=False
        row=event.GetRow()
        col=event.GetCol()

        # If we're entering data in a new row or a new column, append the necessary number of new rows and/or columns to the data source
        self.ExpandDataSourceToInclude(row, col)

        newVal=self._grid.GetCellValue(row, col)
        self._datasource[row][col]=newVal
        #Log("set datasource("+str(row)+", "+str(col)+")="+newVal)
        self.ColorCellByValue(row, col)
        self.RefreshWxGridFromDatasource()
        self.AutoSizeColumns()

    # ------------------
    def OnGridEditorShown(self, event):        # DataGrid
        irow=event.GetRow()
        icol=event.GetCol()
        if self.Datasource.ColDefs[icol].IsEditable == "no":
            event.Veto()
            return
        if self.Datasource.ColDefs[icol].IsEditable == "maybe":
            if (irow, icol) not in self.Datasource.AllowCellEdits:
                event.Veto()

    # ------------------
    def OnGridLabelLeftClick(self, event):        # DataGrid
        self.SaveClickLocation(event)

        if self.clickedColumn >= 0:
            self._grid.ClearSelection()
            self._grid.SelectCol(self.clickedColumn)

        if self.clickedRow >= 0:
            self._grid.ClearSelection()
            self._grid.SelectRow(self.clickedRow)


    def DefaultPopupEnabler(self, event, popup) -> None:        # DataGrid
        self.SaveClickLocation(event)

        # Set everything to disabled.
        for mi in popup.GetMenuItems():
            mi.Enable(False)

        # Everything remains disabled when we're outside the defined columns
        if self.clickedColumn > len(self._datasource.ColDefs)+1:
            return

        # We enable the Copy item if have a selection
        if self.HasSelection():
            mi=popup.FindItemById(popup.FindItem("Copy"))
            mi.Enable(True)

        # We enable the Paste popup menu item if there is something to paste
        mi=popup.FindItemById(popup.FindItem("Paste"))
        mi.Enabled=self.clipboard is not None and len(self.clipboard) > 0 and len(self.clipboard[0]) > 0  # Enable only if the clipboard contains actual content


    # ------------------
    def OnGridLabelRightClick(self, event, m_GridLabelPopup):        # DataGrid
        if m_GridLabelPopup is None:
            event.skip()
        self.DefaultPopupEnabler(event, m_GridLabelPopup)


    #------------------
    # This records the column and row and disables all the popup menu items
    # Then it enables copy and paste if appropriate.
    # Further handling is the responsibility of the application which called it
    def OnGridCellRightClick(self, event, m_GridPopup):        # DataGrid
        self.DefaultPopupEnabler(event, m_GridPopup)


    #-------------------
    def OnGridCellDoubleClick(self, event):        # DataGrid
        self.SaveClickLocation(event)
        #TODO: Is this all?


    #-------------------
    # Locate the selection, real or implied
    # There are three cases, in descending order of preference:
    #   There is a selection block defined
    #   There is a SelectedCells defined
    #   There is a GridCursor location
    def LocateSelection(self) -> tuple[int, int, int, int]:        # DataGrid
        if len(self._grid.SelectionBlockTopLeft) > 0 and len(self._grid.SelectionBlockBottomRight) > 0:
            top, left=self._grid.SelectionBlockTopLeft[0]
            bottom, right=self._grid.SelectionBlockBottomRight[0]
        elif len(self._grid.SelectedCells) > 0:
            top, left=self._grid.SelectedCells[0]
            bottom, right=top, left
        else:
            left=right=self._grid.GridCursorCol
            top=bottom=self._grid.GridCursorRow
        return top, left, bottom, right


    def HasSelection(self) -> bool:        # DataGrid
        if len(self._grid.SelectionBlockTopLeft) > 0 and len(self._grid.SelectionBlockBottomRight) > 0:
            return True
        if len(self._grid.SelectedCells) > 0:
            return True
        return False


    def SelectRows(self, top, bottom) -> None:        # DataGrid
        self._grid.SelectRow(top)
        for i in range(top+1, bottom+1):
            self._grid.SelectRow(i, addToSelected = True)

    def SelectCols(self, left, right) -> None:        # DataGrid
        self._grid.SelectCol(left)
        for i in range(left+1, right+1):
            self._grid.SelectCol(i, addToSelected = True)

    # Return a box which bounds all selections in the grid
    # Top, Left, Bottom, Right
    def SelectionBoundingBox(self) -> Optional[tuple[int, int, int, int]]:        # DataGrid
        if len(self._grid.SelectionBlockTopLeft) == 0:
            return -1, -1, -1, -1
        top=99999
        left=99999
        for t, l in self._grid.SelectionBlockTopLeft:
            top=min(top, t)
            left=min(left, l)
        bottom=-1
        right=-1
        for b, r in self._grid.SelectionBlockBottomRight:
            bottom=max(bottom, b)
            right=max(right, r)

        return top, left, bottom, right

    # Take the existing selected cells and extend the selection to the full rows
    def ExtendRowSelection(self) -> tuple[int, int]:        # DataGrid
        if len(self._grid.SelectionBlockTopLeft) == 0:
            return -1, -1
        top, _, bottom, _=self.SelectionBoundingBox()
        self.SelectRows(top, bottom)
        return top, bottom

    # Take the existing selected cells and extend the selection to the full columns
    def ExtendColSelection(self) -> tuple[int, int]:        # DataGrid
        if len(self._grid.SelectionBlockTopLeft) == 0:
            return -1, -1
        _, left, _, right=self.SelectionBoundingBox()
        self.SelectCols(left, right)
        return left, right

    #-------------------
    def OnKeyDown(self, event):        # DataGrid
        top, left, bottom, right=self.LocateSelection()

        if event.KeyCode == 67 and self.cntlDown:   # cntl-C
            self.CopyCells(top, left, bottom, right)

        elif event.KeyCode == 86 and self.cntlDown and self.clipboard is not None and len(self.clipboard) > 0: # cntl-V
            self.PasteCells(top, left)

        elif event.KeyCode == 308:                  # cntl key alone
            self.cntlDown=True
            print("cntlDown=True")

        elif event.KeyCode == 68:                   # Kludge to be able to force a refresh (press "d")
            self.RefreshWxGridFromDatasource()

        elif event.KeyCode == 314 and self.HasSelection():      # Left arrow
            #print("**move left")
            left, right=self.ExtendColSelection()
            if right != -1:   # There must be a selection
                if left > 0: # Can move left only if the first col selected is not col 0
                    self.MoveCols(left, right-left+1, left-1)     # And move 'em left 1
                    self.SelectCols(left-1, right-1)
                    self.RefreshWxGridFromDatasource()

        elif event.KeyCode == 315 and self.HasSelection():      # Up arrow
            top, bottom=self.ExtendRowSelection()
            if top != -1:   # There must be a selection
                if top > 0:  # Can move up only if the first row selected is not row 0
                    self.MoveRows(top, bottom-top+1, top-1)     # And move 'em up 1
                    self.SelectRows(top-1, bottom-1)
                    self.RefreshWxGridFromDatasource()

        elif event.KeyCode == 316 and self.HasSelection():      # Right arrow
            #print("**move right")
            left, right=self.ExtendColSelection()
            if right != -1:   # There must be a selection
                if right < self._grid.NumberCols-1:    # Can move further right only if the rightmost col is not selected
                    self.MoveCols(left, right-left+1, left+1)     # And move 'em up 1
                    self.SelectCols(left+1, right+1)
                    self.RefreshWxGridFromDatasource()

        elif event.KeyCode == 317 and self.HasSelection():      # Down arrow
            top, bottom=self.ExtendRowSelection()
            if top != -1:   # There must be a selection
                if bottom < self._grid.NumberRows-1:      # Can move further down only if the bottom row is not selected
                    self.MoveRows(top, bottom-top+1, top+1)     # And move 'em up 1
                    self.SelectRows(top+1, bottom+1)
                    self.RefreshWxGridFromDatasource()

        else:
            event.Skip()

    #-------------------
    def OnKeyUp(self, event):        # DataGrid
        if event.KeyCode == 308:                    # cntl
            self.cntlDown=False
            print("cntlDown=False")


    #------------------
    # Copy the selected cells into the clipboard object.
    def OnPopupCopy(self, event):        # DataGrid
        self._grid.SaveEditControlValue()
        # (We can't simply store the coordinates because the user might edit the cells before pasting.)
        top, left, bottom, right=self.LocateSelection()
        self.CopyCells(top, left, bottom, right)
        self.RefreshWxGridFromDatasource()


    #------------------
    # Paste the cells on the clipboard into the grid at the click location
    def OnPopupPaste(self, event):        # DataGrid
        self._grid.SaveEditControlValue()
        top, left, _, _=self.LocateSelection()
        self.PasteCells(top, left)
        self.RefreshWxGridFromDatasource()


    def OnPopupEraseSelection(self, event):        # DataGrid
        self._grid.SaveEditControlValue()
        top, left, bottom, right=self.Datasource.LimitBoxToActuals(self.LocateSelection())
        for irow in range(top, bottom+1):
            for icol in range (left, right+1):
                self.Datasource[irow][icol]=""
        self.RefreshWxGridFromDatasource()


    # Delete the selected columns
    def DeleteSelectedColumns(self):        # DataGrid
        self._grid.SaveEditControlValue()
        _, left, _, right=self.SelectionBoundingBox()
        if left == -1 or right == -1:
            del self.Datasource.ColDefs[self.clickedColumn]
            for i, row in enumerate(self.Datasource.Rows):
                row.DelCol(self.clickedColumn)
        else:
            icols=slice(left, right+1)
            del self.Datasource.ColDefs[icols]
            for i, row in enumerate(self.Datasource.Rows):
                row.DelCol(icols)
        self._grid.ClearSelection()
        self.RefreshWxGridFromDatasource()


    def DeleteSelectedRows(self):        # DataGrid
        self._grid.SaveEditControlValue()
        top, _, bottom, _=self.SelectionBoundingBox()
        if top == -1 or bottom == -1:
            top=self.clickedRow
            bottom=self.clickedRow
        del self.Datasource.Rows[top:bottom+1]
        self._grid.ClearSelection()
        self.RefreshWxGridFromDatasource()


    def OnPopupRenameCol(self, event):        # DataGrid
        self._grid.SaveEditControlValue()
        v=MessageBoxInput("Enter the new column name", title="Renaming column", ignoredebugger=True)
        if v is not None:
            icol=self.clickedColumn
            self.Datasource.ColDefs[icol].Name=v
            self.RefreshWxGridFromDatasource()


    def InsertColumnMaybeQuery(self, icol: int, name: str= "") -> None:        # DataGrid
        self._grid.SaveEditControlValue()
        if name == "":
            name=MessageBoxInput("Enter the new column's name", title="Inserting column", ignoredebugger=True)
            if name is None or len(name.strip()) == 0:
                #event.Skip()
                return

        for row in self.Datasource.Rows:
            row._cells=row._cells[:icol+1]+[""]+row._cells[icol+1:]
        self.Datasource.ColDefs=self.Datasource.ColDefs[:icol+1]+ColDefinitionsList([ColDefinition(name)])+self.Datasource.ColDefs[icol+1:]
        self.RefreshWxGridFromDatasource()


    def OnPopupInsertColLeft(self, event):        # DataGrid
        self._grid.SaveEditControlValue()
        self.InsertColumnMaybeQuery(self.clickedColumn-1)

    def OnPopupInsertColRight(self, event):        # DataGrid
        self._grid.SaveEditControlValue()
        self.InsertColumnMaybeQuery(self.clickedColumn)

    # ------------------
    def HideRowLabels(self) -> None:        # DataGrid
        self._grid.HideRowLabels()
