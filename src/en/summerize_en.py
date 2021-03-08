from modules_en import SCP, MarkdownWriter, GraphDataWriter

if __name__ == '__main__':
    scp = SCP('../../yaml/en/')

    path = '../../'
    mdw = MarkdownWriter(scp, path)
    mdw.save_to_markdown()

    gdw = GraphDataWriter(scp, path + '../../graph/en/')
    gdw.save_to_csv()
