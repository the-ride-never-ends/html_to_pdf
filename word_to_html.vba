Sub ConvertWordToHTML()
    Dim doc As Document
    Dim htmlDoc As String
    Dim para As Paragraph
    Dim citation As Field
    Dim endnote As Endnote
    Dim htmlFilePath As String
    Dim fs As Object
    Dim htmlFile As Object
    Dim listStarted As Boolean

    ' Set the document object to the active Word document
    Set doc = ActiveDocument

    ' Initialize the HTML string with basic structure
    htmlDoc = "<html><head><title>" & doc.Name & "</title></head><body>"
    
    ' Initialize variable to check if list is active
    listStarted = False

    ' Loop through each paragraph in the document
    For Each para In doc.Paragraphs
        ' Check if the paragraph is part of a list
        If para.Range.ListFormat.ListType = wdListBullet Then
            ' Start a bullet list if not started
            If Not listStarted Then
                htmlDoc = htmlDoc & "<ul>"
                listStarted = True
            End If
            ' Add the bullet item
            htmlDoc = htmlDoc & "<li>" & para.Range.Text & "</li>"
        ElseIf para.Range.ListFormat.ListType = wdListSimpleNumbering Then
            ' Start a numbered list if not started
            If Not listStarted Then
                htmlDoc = htmlDoc & "<ol>"
                listStarted = True
            End If
            ' Add the numbered item
            htmlDoc = htmlDoc & "<li>" & para.Range.Text & "</li>"
        Else
            ' Close any open list tags if the paragraph is not part of a list
            If listStarted Then
                If para.Range.ListFormat.ListType = wdListBullet Then
                    htmlDoc = htmlDoc & "</ul>"
                ElseIf para.Range.ListFormat.ListType = wdListSimpleNumbering Then
                    htmlDoc = htmlDoc & "</ol>"
                End If
                listStarted = False
            End If
            ' For regular paragraphs, convert to <p> tags
            htmlDoc = htmlDoc & "<p>" & para.Range.Text & "</p>"
        End If
    Next para

    ' Close any remaining open list tags at the end of the document
    If listStarted Then
        If doc.Paragraphs.Last.Range.ListFormat.ListType = wdListBullet Then
            htmlDoc = htmlDoc & "</ul>"
        ElseIf doc.Paragraphs.Last.Range.ListFormat.ListType = wdListSimpleNumbering Then
            htmlDoc = htmlDoc & "</ol>"
        End If
    End If

    ' Loop through each citation field
    For Each citation In doc.Fields
        If citation.Type = wdFieldCitation Then
            ' Wrap citation text in a span with a "citation" class
            htmlDoc = Replace(htmlDoc, citation.Code.Text, "<span class='citation'>" & citation.Code.Text & "</span>")
        End If
    Next citation

    ' Add endnotes to the end of the HTML document
    If doc.Endnotes.Count > 0 Then
        htmlDoc = htmlDoc & "<h2>Endnotes</h2><ol>"
        For Each endnote In doc.Endnotes
            htmlDoc = htmlDoc & "<li>" & endnote.Range.Text & "</li>"
        Next endnote
        htmlDoc = htmlDoc & "</ol>"
    End If

    ' Close the HTML structure
    htmlDoc = htmlDoc & "</body></html>"

    ' Define the path to save the HTML file
    htmlFilePath = doc.Path & "\" & Replace(doc.Name, ".docx", ".html")

    ' Create the file system object and write the HTML string to a file
    Set fs = CreateObject("Scripting.FileSystemObject")
    Set htmlFile = fs.CreateTextFile(htmlFilePath, True)
    htmlFile.WriteLine htmlDoc
    htmlFile.Close

    ' Inform the user
    MsgBox "HTML file created at: " & htmlFilePath

End Sub